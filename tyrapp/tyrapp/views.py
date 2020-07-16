from tyrapp import app
from tyrapp import mongo, LDA
from tyrapp import munge as Munge
from tyrapp import archiver as Archiver
from flask import render_template, request, redirect, send_from_directory, safe_join, abort
from werkzeug.utils import secure_filename
import os
import pymongo
import csv
import sys
import zipfile
from gensim import models
from multiprocessing import Pool

# rather than deconstructing and reconstructing object ids through strings, 
# we are simply pickling and unpickling those object ids
# from bson.objectid import ObjectId

app_root = app.config['APP_ROOT']

get_served = os.path.join(app_root, 'get_served')

Archiver.cleanup()

pool = Pool(os.cpu_count() - 1)
doc_num = 1000
data_path = app.config["DATA_PATH"]
csv_path = os.path.join(data_path, 'data.csv')
print("Populating dictionary")
corpus_dictionary = LDA.create_dict(csv_path, doc_num)
print("Loading model to server")
model = models.LdaModel.load(LDA.model_file)
bow_corpus = LDA.CaseCorpus(csv_path, corpus_dictionary)
lda_corpus = model[bow_corpus]

print("Connecting to database")
client = pymongo.MongoClient("mongodb://localhost:27017/")
tyr_db = client["tyr_db"]
cases_collection = tyr_db["cases"]


@app.route("/")
def index():
    print("Here I am!")
    return render_template("public/index.html", active_id="home")


@app.route("/about")
def about():
    return render_template("public/about.html", active_id = "about")

def allowed_file(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() == "TXT":
        return True
    else:
        return False


# def allowed_image_filesize(filesize):

#     if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
#         return True
#     else:
#         return False


@app.route("/search", methods=["GET", "POST"])
def search():

    if request.method == "POST":

        if request.files:

            # if not allowed_image_filesize(request.cookies.get("filesize")):
            #     print("File exceeded maximum size.")
            #     return request(request.url)

            text = request.files["text"]

            if text.filename == "":
                print("File must have a filename.")
                return redirect(request.url)

            if not allowed_file(text.filename):
                print("That extension is not allowed.")
                return redirect(request.url)
            else:
                Archiver.cleanup()
                filename = secure_filename(text.filename)
                filepath = os.path.join(app.config["UPLOADS"], filename)
                text.save(filepath)
                print("Document saved")
                with open(filepath) as doc:
                    doc_text = doc.read()
                print(f"Scrubbing Punctuation from {filename}")
                scrubbed_text = Munge.scrubPunct(doc_text)
                print(f"Tokenizing {filename}")
                tokens = Munge.tokenize(scrubbed_text)
                print(f"Lemmatizing {filename}")
                lemmatized = Munge.lemmatize(tokens)
                print(f"Removing Stopwords from {filename}")
                stopless = Munge.removeStops(lemmatized)
                print("Running Hellinger Query")
                object_ids = LDA.query_hellinger(stopless, lda_corpus, model, threshold = 0.5)
                docs_iter = cases_collection.find({'_id': {'$in': object_ids}})
                docs_list = [doc for doc in docs_iter]
                print("Writing corpus to directory")
                Archiver.write_list_to_TXTs(docs_list)
                filename_list = os.listdir(get_served)
                print("Zipping corpus directory")
                Archiver.zip_list_of_files(filename_list, get_served, 'out.zip')
                print("Sending zipfile")
                return send_from_directory(get_served,filename='out.zip', as_attachment=True)

            return redirect(request.url)

    return render_template("public/search.html", active_id="search")
