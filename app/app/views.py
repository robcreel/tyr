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

def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


# def allowed_image_filesize(filesize):

#     if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
#         return True
#     else:
#         return False


@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():

    if request.method == "POST":

        if request.files:

            # if not allowed_image_filesize(request.cookies.get("filesize")):
            #     print("File exceeded maximum size.")
            #     return request(request.url)

            image = request.files["image"]


            if image.filename == "":
                print("Image must have a filename.")
                return redirect(request.url)

            if not allowed_image(image.filename):
                print("That extension is not allowed.")
                return redirect(request.url)
            
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
       
                print("Image saved")


            return redirect(request.url)


    return render_template("public/upload_image.html")


#################################
# 
#       View for PyMongo:
# 
#################################

@app.route("/himongo", methods=['GET', 'POST', 'DELETE', 'PATCH'])
def himongo():
    teammates = mongo.db.Avengers.find_one({"Name": "Tony Stark"})
    return f"<h1> One Marvel hero is {teammates['Made-up_Name']}.</h1>"



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

    # Function to get first n items in a list, if there are that many.
    def get_top_n(input_list, n):
        n = min(n, len(input_list))
        return(input_list[:n])

    # Function to write a single dictionary to a CSV
    def write_dict_to_CSV(input_dict, filename = "data", destination_path = "./get_served"):
        with open(f"{destination_path}/file_{filename}.csv", "w") as f:
            for key in input_dict.keys():
                f.write("%s, %s\n" % (key, input_dict[key]))

    # Function to write a list of dictionaries to CSVs
    def write_dict_list_to_CSVs(input_list, destination_path = "./get_served"):
        for i in range(len(input_list)):
            write_dict_to_CSV(input_list[i], str(i + 1), destination_path)


    # Function to zip a list of files.
    def zip_list_of_files(input_list, destination_path, filename):
        with zipfile.ZipFile(f"{destination_path}/{filename}", 'w') as zipMe:        
            for file in input_list:
            # filepath = f"./get_served/{file}"
                zipMe.write(file, compress_type=zipfile.ZIP_DEFLATED)
    
    write_dict_list_to_CSVs(yourlist, app.config["CLIENT_DIRECTORY"])
    temporary_list = os.listdir(app.config["CLIENT_DIRECTORY"])
    print(temporary_list)
    os.chdir(app.config["CLIENT_DIRECTORY"])
    zip_list_of_files(temporary_list, app.config["CLIENT_DIRECTORY"], "out.zip")
    for file in temporary_list:
        os.remove(file)
    # os.chdir("..")

    # return_this_file = "serve_me.txt"
    return_this_file = "out.zip"

    try:
        return send_from_directory(app.config["CLIENT_DIRECTORY"], filename=return_this_file, as_attachment=True)
    except FileNotFoundError:
        abort(404)


