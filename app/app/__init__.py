from flask import Flask

# app = Flask(__name__)

from app import views
from app import admin_views

from .extensions import mongo
from .main import main

def create_app(config_object='app.settings'):
    app = Flask(__name__)

    app.config.from_object(config_object)

    mongo.init_app(app)

    app.register_blueprint(main)
    
    return app