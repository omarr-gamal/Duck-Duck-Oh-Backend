#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import (Flask, jsonify, request)
from flask_moment import Moment

from models import *


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_pyfile('config.py')

db.init_app(app)


#----------------------------------------------------------------------------#
# Routes.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    return jsonify({
        'search_engine': True
    }), 200
 

@app.route('/documents', methods=['POST'])
def create_document():
    pass

    
@app.route('/init')
def init():
    db.engine.execute("DROP SCHEMA public CASCADE;")
    db.engine.execute("CREATE SCHEMA public;")

    db.create_all(app=app)
    
    return jsonify({
        'success': True
    }), 200
    

#----------------------------------------------------------------------------#
# Error Handlers.
#----------------------------------------------------------------------------#

@app.errorhandler(400)
def error_400(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': error.description
    }), 400

@app.errorhandler(404)
def error_404(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': error.description
    }), 404

@app.errorhandler(500)
def error_500(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': error.description
    }), 500


#----------------------------------------------------------------------------#
# Launch
#----------------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=False)