#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import (Flask, jsonify, request, abort)
from flask_moment import Moment

from models import *
from engine import Engine

from request_errors import requires_body, requires_args

from spellchecker import SpellChecker


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_pyfile('config.py')

db.init_app(app)

with app.app_context():
    engine = Engine()

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
    
    Document('This is a document about cats.').insert()
    Document('This is a document about dogs.').insert()
    Document('This is a document about mcats and dogs.').insert()
    Document('This is a document about catm and dogs.').insert()
    Document('This is a document about mcat and dogs.').insert()
    Document('This is a document about cats cats cats cat.').insert()
    Document('This is a document about cat cat cat cat.').insert()
    Document('This is a document about dog.').insert()
    Document('This is a document about catsdogs.').insert()
    Document('This is a document about elephants.').insert()
    
    engine.index_all_documents()
    
    return jsonify({
        'success': True
    }), 200
    

@app.route('/documents', methods=['POST'])
@requires_body('body')
def create_document():
    body = request.get_json().get('body')
    
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
    
    results = engine.search(query)
    
    return jsonify({
        'success': True,
        'results': [Document.query.get(result).format() for result in results]
    }), 200
    
@app.route('/search/images', methods=['get'])
@requires_args('query')
def search_images():
    query = request.args.get('query')
    
    results = engine.search_images(query)
    
    return jsonify({
        'success': True,
        'results': results
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
