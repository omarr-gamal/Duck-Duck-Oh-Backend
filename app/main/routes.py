from flask import request, abort, current_app
from apifairy import response, body, arguments, other_responses
from spellchecker import SpellChecker
import secrets
from flask_limiter.util import get_remote_address

from ..models import Document, ApiKey
from ..extensions import db, limiter
from ..engine import engine
from ..schemas import (
    HealthCheckSchema,
    DocumentBodySchema,
    DocumentResponseSchema,
    SearchQuerySchema,
    SearchResponseSchema,
    ImageSearchResponseSchema,
    ErrorSchema,
    ApiKeySchema,
    ApiKeyResponseSchema,
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


def get_api_key():
    """Custom key function for rate limiting"""
    api_key = request.headers.get("X-API-KEY")
    if api_key:
        # Verify if the key exists in the database
        key_obj = db.session.query(ApiKey).filter_by(key=api_key).first()
        if key_obj:
            return api_key
    return get_remote_address()


def rate_limit_key():
    """Determine rate limit based on API key presence"""
    api_key = request.headers.get("X-API-KEY")
    if api_key:
        # Verify if the key exists in the database
        key_obj = db.session.query(ApiKey).filter_by(key=api_key).first()
        if key_obj:
            return current_app.config.get("RATELIMIT_AUTHENTICATED", "20 per minute")
    return current_app.config.get("RATELIMIT_GUEST", "10 per minute")


@main.route("/api/keys", methods=["POST"])
@body(ApiKeySchema)
@response(ApiKeyResponseSchema, 201)
@other_responses({400: ErrorSchema, 500: ErrorSchema})
def create_api_key(body_data):
    """Create a new API key
    
    Generate a new API key for accessing the API with higher rate limits
    """
    description = body_data.get("description")
    key = secrets.token_urlsafe(32)
    
    api_key = ApiKey(key=key, description=description)
    api_key.insert()
    
    return {"success": True, "api_key": api_key}


@main.route("/")
@response(HealthCheckSchema)
@other_responses({500: ErrorSchema})
def index():
    """Health check endpoint

    Check if the search engine API is running
    """
    return {"search_engine": True}


@main.route("/documents", methods=["POST"])
@limiter.limit(rate_limit_key, key_func=get_api_key)
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
@limiter.limit(rate_limit_key, key_func=get_api_key)
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
@limiter.limit(rate_limit_key, key_func=get_api_key)
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
@limiter.limit(rate_limit_key, key_func=get_api_key)
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
