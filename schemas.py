"""
Marshmallow schemas for request/response serialization and validation
"""

from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, validate, EXCLUDE

# ma initialized in app.py
ma = Marshmallow()


class HealthCheckSchema(ma.Schema):
    """Health check response schema"""

    search_engine = fields.Bool(required=True)


class SuccessSchema(ma.Schema):
    """Generic success response schema"""

    success = fields.Bool(required=True)


class DocumentBodySchema(ma.Schema):
    """Schema for document creation request"""

    body = fields.Str(required=True, validate=validate.Length(min=1))

    class Meta:
        unknown = EXCLUDE


class DocumentSchema(ma.Schema):
    """Schema for document response"""

    id = fields.Int(required=True)
    body = fields.Str(required=True)
    added_at = fields.DateTime(required=True)


class DocumentResponseSchema(ma.Schema):
    """Schema for single document response"""

    success = fields.Bool(required=True)
    document = fields.Nested(DocumentSchema, required=True)


class SearchQuerySchema(ma.Schema):
    """Schema for search query parameters"""

    query = fields.Str(required=True, validate=validate.Length(min=1))
    no_spell_check = fields.Bool(
        load_default=False,
        metadata={
            "description": "Set to true to disable spell checking for search queries."
        },
    )

    class Meta:
        unknown = EXCLUDE


class SearchResultSchema(ma.Schema):
    """Schema for individual search result"""

    id = fields.Int(required=True)
    title = fields.Str(required=True, allow_none=True)
    body = fields.Str(required=True)
    added_at = fields.DateTime(required=True)
    outline = fields.Str(required=True, allow_none=True)


class SearchResponseSchema(ma.Schema):
    """Schema for search results response"""

    success = fields.Bool(required=True)
    results = fields.List(fields.Nested(SearchResultSchema), required=True)
    query = fields.Str(required=True)


class ImageSearchResultSchema(ma.Schema):
    """Schema for image search result"""

    # Adjust these fields based on what engine.search_images() returns
    url = fields.Str(required=True)
    title = fields.Str(allow_none=True)
    thumbnail = fields.Str(allow_none=True)


class ImageSearchResponseSchema(ma.Schema):
    """Schema for image search results response"""

    success = fields.Bool(required=True)
    results = fields.List(fields.Nested(ImageSearchResultSchema), required=True)
    query = fields.Str(required=True)


class ErrorSchema(ma.Schema):
    """Schema for error responses"""

    success = fields.Bool(required=True)
    error = fields.Int(required=True)
    message = fields.Str(required=True)
