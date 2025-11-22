import os

SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# APIFairy
APIFAIRY_TITLE = "Duck Duck Oh API"
APIFAIRY_VERSION = "1.0"
APIFAIRY_UI = "elements"

# SQLite in-memory db
SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
SQLALCHEMY_TRACK_MODIFICATIONS = False

TESTING = True
