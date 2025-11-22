from flask import request, abort
from apifairy import response, body, arguments, other_responses
from spellchecker import SpellChecker

from ..models import Document
from ..extensions import db
from ..engine import engine
from ..schemas import (
    HealthCheckSchema,
    DocumentBodySchema,
    DocumentResponseSchema,
    SearchQuerySchema,
    SearchResponseSchema,
    ImageSearchResponseSchema,
    ErrorSchema,
)
from . import main


@main.after_request
def after_request(response):
    origin = request.headers.get("Origin")
    response.headers.add("Access-Control-Allow-Origin", origin)
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add(
        "Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS"
    )
    return response


@main.route("/")
@response(HealthCheckSchema)
@other_responses({500: ErrorSchema})
def index():
    """Health check endpoint

    Check if the search engine API is running
    """
    return {"search_engine": True}


@main.route("/documents", methods=["POST"])
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


@main.route("/documents/<int:document_id>", methods=["GET"])
@response(DocumentResponseSchema)
@other_responses({400: ErrorSchema, 404: ErrorSchema, 500: ErrorSchema})
def get_document(document_id):
    """Get a document by ID

    Retrieve a specific document from the database
    """
    document = db.session.get(Document, document_id)

    if not document:
        abort(404, "Document not found")

    return {"success": True, "document": document}


@main.route("/search", methods=["GET"])
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

    results = [db.session.get(Document, doc_id) for doc_id in engine.search(query)]

    return {"success": True, "results": results, "query": query}


@main.route("/search/images", methods=["GET"])
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
