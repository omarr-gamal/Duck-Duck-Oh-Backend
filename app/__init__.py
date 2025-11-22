from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, ma, apifairy, moment
from .main import main as main_blueprint
from .commands import download_nltk, populate_db_cmd, reset_db_cmd

def create_app(config_file="config.py"):
    app = Flask(__name__)
    
    app.config.from_pyfile(config_file)
    
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    apifairy.init_app(app)
    moment.init_app(app)
    
    CORS(app, resources={r"*/api/*": {"origins": "*"}})
    
    app.register_blueprint(main_blueprint)
    
    app.cli.add_command(download_nltk)
    app.cli.add_command(populate_db_cmd)
    app.cli.add_command(reset_db_cmd)
    
    return app
