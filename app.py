"""
Python Search Engine built using Flask and SQLAlchemy that indexes HTML documents
and applies tokenization and stemming to search, and TF-IDF vectorization and
Cosine Similarity to rank the documents by relevance to search query.
"""

# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
import click

from flask import Flask, abort, request
from flask_moment import Moment
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from apifairy import APIFairy, response, body, arguments, other_responses

from models import db, migrate, Document, Index
from engine import engine
from schemas import (
    HealthCheckSchema,
    SuccessSchema,
    DocumentBodySchema,
    DocumentResponseSchema,
    SearchQuerySchema,
    SearchResponseSchema,
    ImageSearchResponseSchema,
    ErrorSchema,
)

from spellchecker import SpellChecker

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)

app.config.from_pyfile("config.py")

db.init_app(app)
migrate.init_app(app, db)

ma = Marshmallow(app)
apifairy = APIFairy(app)

CORS(app, resources={r"*/api/*": {"origins": "*"}})

# ----------------------------------------------------------------------------#
# Routes.
# ----------------------------------------------------------------------------#


@app.after_request
def after_request(response):
    origin = request.headers.get("Origin")
    response.headers.add("Access-Control-Allow-Origin", origin)
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add(
        "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
    )
    return response


@app.cli.command("download_nltk")
def download_nltk():
    """Download NLTK dictionaries"""
    engine.download_nltk_dicts()
    click.echo("NLTK dictionaries downloaded.")


@app.cli.command("populate_db")
def populate_db_cmd():
    """Populate the database."""
    if not Document.query.first() and not Index.query.first():
        import init_db

        click.echo("Database populated.")


@app.cli.command("reset_db")
def reset_db_cmd():
    """Reset the database."""
    db.drop_all()
    db.create_all()
    click.echo("Database reset.")


@app.route("/")
@response(HealthCheckSchema)
@other_responses({500: ErrorSchema})
def index():
    """Health check endpoint

    Check if the search engine API is running
    """
    return {"search_engine": True}


@app.route("/init")
@response(SuccessSchema)
@other_responses({500: ErrorSchema})
def init():
    """Initialize database

    Drop and recreate the database schema, then populate with initial data
    """
    db.engine.execute("DROP SCHEMA public CASCADE;")
    db.engine.execute("CREATE SCHEMA public;")

    db.create_all(app=app)

    import init_db

    global engine
    engine = Engine()

    return {"success": True}


@app.route("/documents", methods=["POST"])
@body(DocumentBodySchema)
@response(DocumentResponseSchema, 200)
@other_responses({400: ErrorSchema, 500: ErrorSchema})
def create_document(body_data):
    """Create a new document

    Add a new HTML document to the search engine index
    """
    body = body_data["body"]
    document = engine.add_document(body)

    return {"success": True, "document": document}


@app.route("/documents/<int:document_id>", methods=["GET"])
@response(DocumentResponseSchema)
@other_responses({400: ErrorSchema, 404: ErrorSchema, 500: ErrorSchema})
def get_document(document_id):
    """Get a document by ID

    Retrieve a specific document from the database
    """
    document = Document.query.get(document_id)

    if not document:
        abort(404, "Document not found")

    return {"success": True, "document": document}


@app.route("/search", methods=["GET"])
@arguments(SearchQuerySchema, location="query")
@response(SearchResponseSchema)
@other_responses({400: ErrorSchema, 500: ErrorSchema})
def search_documents(query_params):
    """Search documents

    Search indexed documents using the provided query with optional spell checking
    """
    query = query_params["query"]
    no_spell_check = query_params.get("no_spell_check", False)

    if not no_spell_check:
        spell_checker = SpellChecker()
        query = " ".join([spell_checker.correction(word) for word in query.split(" ")])

    results = [Document.query.get(doc_id) for doc_id in engine.search(query)]

    return {"success": True, "results": results, "query": query}


@app.route("/search/images", methods=["GET"])
@arguments(SearchQuerySchema, location="query")
@response(ImageSearchResponseSchema)
@other_responses({400: ErrorSchema, 500: ErrorSchema})
def search_images(query_params):
    """Search images

    Search for images using the provided query with optional spell checking
    """
    query = query_params["query"]
    no_spell_check = query_params.get("no_spell_check", False)

    if not no_spell_check:
        spell_checker = SpellChecker()
        query = " ".join([spell_checker.correction(word) for word in query.split(" ")])

    results = engine.search_images(query)

    return {"success": True, "results": results, "query": query}


# ----------------------------------------------------------------------------#
# Error Handlers.
# ----------------------------------------------------------------------------#


@app.errorhandler(400)
def error_400(error):
    return {"success": False, "error": 400, "message": error.description}, 400


@app.errorhandler(404)
def error_404(error):
    return {"success": False, "error": 404, "message": error.description}, 404


@app.errorhandler(500)
def error_500(error):
    return {"success": False, "error": 500, "message": error.description}, 500


# ----------------------------------------------------------------------------#
# Launch
# ----------------------------------------------------------------------------#

if __name__ == "__main__":
    app.run(debug=False)
