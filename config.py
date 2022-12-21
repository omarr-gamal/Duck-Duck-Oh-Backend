import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

PROFILE_PICTURE_BASE_URL = 'https://cine-app-profile-images-bucket.s3.amazonaws.com/'

# Auth0 configuration

AUTH0_DOMAIN = os.environ['auth0_domain']

API_AUDIENCE = os.environ['api_audience']
MANAGEMENT_API_AUDIENCE = os.environ['management_api_audience']

CLIENT_ID = os.environ['client_id']
CLIENT_SECRET = os.environ['client_secret']

MANAGEMENT_CLIENT_ID = os.environ['management_client_id']
MANAGEMENT_CLIENT_SECRET = os.environ['management_client_secret']

ALGORITHMS = [os.environ['algorithms']]

# paymob Credentials

PAYMOB_API_KEY = os.environ['paymob_api_key']
PAYMOB_INTEGRATION_ID = os.environ['paymob_integration_id']
PAYMOB_IFRAME_ID = os.environ['paymob_iframe_id']

# AWS Credentials

S3_REGIION = os.environ['s3_region']

TICKET_QR_ACCESS_KEY_ID = os.environ['ticket_gen_access_key_id']
TICKET_QR_SECRET_ACCESS_KEY = os.environ['ticket_gen_secret_access_key']

PROFILE_PICTURE_UPLOAD_ACCESS_KEY_ID = os.environ['profile_image_upload_access_key_id']
PROFILE_PICTURE_UPLOAD_SECRET_ACCESS_KEY = os.environ['profile_image_upload_secret_access_key']

UPLOAD_PROFILE_PICTURE_ROLE_ARN = os.environ['upload_profile_picture_role_arn']

# TMDB variables
TMDB_API_KEY = os.environ['tmdb_api_key']
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_BASE_IMAGE_URL = 'https://image.tmdb.org/t/p/original'

# Connect to the database

# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@database-1.cvtsabdomssx.me-south-1.rds.amazonaws.com:5432/cine'
SQLALCHEMY_DATABASE_URI = os.environ['db_url']

SQLALCHEMY_TRACK_MODIFICATIONS = False
