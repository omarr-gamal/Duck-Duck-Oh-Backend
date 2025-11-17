import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

SQLALCHEMY_DATABASE_URI = ''

if os.environ.get('ENV', "dev") == 'prod':
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres', 'postgresql')
else:
    db_user = os.environ.get('DB_USER', "postgres")
    db_pass = os.environ.get('DB_PASS', "postgres")
    db_name = os.environ.get('DB_NAME', "duck_duck_oh")
    db_base_url = os.environ.get('DB_BASE_URL', "localhost:5432")

    SQLALCHEMY_DATABASE_URI = f'postgresql://{db_user}:{db_pass}@{db_base_url}/{db_name}'

SQLALCHEMY_TRACK_MODIFICATIONS = False

