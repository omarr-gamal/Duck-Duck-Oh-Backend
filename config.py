import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

db_user = os.environ['DB_USER']
db_pass = os.environ['DB_PASS']

SQLALCHEMY_DATABASE_URI = f'postgresql://{db_user}:{db_pass}@localhost:5432/duck_duck_oh'
# SQLALCHEMY_DATABASE_URI = os.environ['db_url']

SQLALCHEMY_TRACK_MODIFICATIONS = False
