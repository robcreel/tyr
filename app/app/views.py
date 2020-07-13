from app import app, mongo
from flask import render_template, request, redirect
from werkzeug.utils import secure_filename
import os

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




# @app.route("zipper")
# def zipper():
