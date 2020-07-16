from app import app, mongo
from flask import render_template, request, redirect, send_from_directory, safe_join, abort
from werkzeug.utils import secure_filename
import os
import pymongo
import csv
import sys
import zipfile
from gensim import models
from multiprocessing import Pool

#rather than deconstructing and reconstructing object ids through strings, 
#we are simply pickling and unpickling those object ids
#from bson.objectid import ObjectId

sys.path.append('./archiver')
sys.path.append('../LDA')
sys.path.append('../munge')
import LDA
import munge as Munge
import archiver as Archiver

Archiver.cleanup()

pool = Pool(os.cpu_count() - 1)
doc_num = 100

corpus_dictionary = LDA.create_dict(LDA.data_path, doc_num)
model = models.LdaModel.load(LDA.model_file)
client = pymongo.MongoClient("mongodb://localhost:27017/")
tyr_db = client["tyr_db"]
cases_collection = tyr_db["cases"]

@app.route("/")
def index():
    return render_template("public/index.html")


@app.route("/about")
def about():
    return "<h1 style='color: red'>About!!!</h1>"

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


@app.route("/upload", methods=["GET", "POST"])
def upload():

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
                
                lda_corpus = LDA.CaseCorpus(LDA.data_path, corpus_dictionary)
                lda_corpus_list = [lda for lda in lda_corpus]
          
                object_ids = LDA.query_hellinger(stopless, lda_corpus, model, threshold = 0.9)
                docs_iter = cases_collection.find({'_id': {'$in': object_ids}})
                docs_list = [doc for doc in docs_iter]
                
                Archiver.write_list_to_TXTs(docs_list)
                filename_list = os.listdir('./get_served')
            
                Archiver.zip_list_of_files(filename_list, './get_served', 'out.zip')
                sent = send_from_directory('./get_served',filename='out.zip', as_attachment=True)
                Archiver.cleanup()
                return sent

                
            return redirect(request.url)

    return render_template("public/upload.html")


# @app.route("/upload/query", methods = ["GET"])
# def query():

#     if request.files:

#         query_text = request.files[""]


app.config["CLIENT_DIRECTORY"] = "/home/rob/Code/tyr/tyr/get_served"

@app.route("/zipper/<int:nn>") #/<int:nn>
def zipper(nn): 

    # client_directory = app.config["CLIENT_DIRECTORY"]


    # setup PyMongo
    

    # Get data
    y = mycol.find().limit(nn)
    yourlist= [each for each in y]

 
    write_dict_list_to_CSVs(yourlist, app.config["CLIENT_DIRECTORY"])
    temporary_list = os.listdir(app.config["CLIENT_DIRECTORY"])
    print(temporary_list)
    os.chdir(app.config["CLIENT_DIRECTORY"])
    zip_list_of_files(temporary_list, app.config["CLIENT_DIRECTORY"], "out.zip")

    
    write_dict_list_to_CSVs(yourlist, app.config["CLIENT_DIRECTORY"])
    temporary_list = os.listdir(app.config["CLIENT_DIRECTORY"])
    print(temporary_list)
    os.chdir(app.config["CLIENT_DIRECTORY"])
    zip_list_of_files(temporary_list, app.config["CLIENT_DIRECTORY"], "out.zip")

    # return_this_file = "serve_me.txt"
    return_this_file = "out.zip"

    try:
        return send_from_directory(app.config["CLIENT_DIRECTORY"], filename=return_this_file, as_attachment=True)
    except FileNotFoundError:
        abort(404)


