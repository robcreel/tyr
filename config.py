class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = "B\xb2?.\xdf\x9f\xa7m\xf8\x8a%,\xf7\xc4\xfa\x91"

    DB_NAME = "production-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"

    # IMAGE_UPLOADS = "/home/rob/Code/rob_attempting_to_splice_python_and_mongo/app/app/app/static/img/uploads"
    UPLOADS = "./app/static/text/uploads"
    # ALLOWED_IMAGE_EXTENSIONS = ["JPEG", "JPG", "PNG", "GIF", "TXT", "CSV"]
    MONGO_URI = "mongodb://127.0.0.1:27017/tyr_db"

    # CLIENT_DIRECTORY = "./get_served/"

    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    DB_NAME = "development-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    TESTING = True
    DB_NAME = "development-db"
    DB_USERNAME = "admin"
    DB_PASSWORD = "example"
    SESSION_COOKIE_SECURE = False
