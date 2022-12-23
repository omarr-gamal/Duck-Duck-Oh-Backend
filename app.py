#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import (Flask, jsonify, request, abort)
from flask_moment import Moment

from models import *

from engine import Engine

from request_errors import requires_body, requires_args


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
    
@app.route('/init')
def init():
    db.engine.execute("DROP SCHEMA public CASCADE;")
    db.engine.execute("CREATE SCHEMA public;")

    db.create_all(app=app)
    
    return jsonify({
        'success': True
    }), 200
    

@app.route('/documents', methods=['POST'])
@requires_body('body')
def create_document():
    body = request.get_json().get('body')
    
    engine = Engine()
    engine.add_document(body)
    
    return jsonify({
        'success': True
    }), 200

@app.route('/documents/<int:document_id>', methods=['get'])
def get_document(document_id):
    document = Document.query.get(document_id)
    
    if not document:
        abort(400, 'Document not found')
    
    return jsonify({
        'success': True,
        'document': document.format()
    }), 200


@app.route('/search', methods=['get'])
@requires_args('query')
def search_documents():
    query = request.args.get('query')
    
    engine = Engine()
    results = engine.search(query)
    
    return jsonify({
        'success': True,
        'results': [Document.query.get(result).format() for result in results]
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