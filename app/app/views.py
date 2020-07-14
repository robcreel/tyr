from app import app, mongo
from flask import render_template, request, redirect, send_from_directory, safe_join, abort
from werkzeug.utils import secure_filename
import os
import pymongo
import csv
import zipfile


@app.route("/")
def index(): 
    return render_template("public/index.html")


@app.route("/jinja")
def jinja():
    return render_template("public/jinja.html")

@app.route("/about")
def about():
    return "<h1 style='color: red'>About!!!</h1>"


# Note see Julian Nash tutorial Part 12 for more on app.config
# app.config["IMAGE_UPLOADS"] = "/home/rob/Code/tyr/tyr/app/app/static/img/uploads"
# app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF", "TXT", "CSV"]
# app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

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
                text.save(os.path.join(app.config["UPLOADS"], text.filename))
       
                print("Document saved")

                """
                TODO Get list of hashcoded from LDA.py, then send those hashcodes to mongo for a list of text documents, which we will write into get_served, and archive.
                """

            return redirect(request.url)

    return render_template("public/upload_image.html")


# @app.route("/upload/query", methods = ["GET"])
# def query():

#     if request.files:

#         query_text = request.files[""]


app.config["CLIENT_DIRECTORY"] = "/home/rob/Code/tyr/tyr/get_served"

@app.route("/zipper/<int:nn>") #/<int:nn>
def zipper(nn): 

    # client_directory = app.config["CLIENT_DIRECTORY"]


    # setup PyMongo
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]
    mycol = mydb["customers"]

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


