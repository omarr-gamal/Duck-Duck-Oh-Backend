from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from apifairy import APIFairy
from flask_moment import Moment

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
apifairy = APIFairy()
moment = Moment()
