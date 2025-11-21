"""
Marshmallow schemas for request/response serialization and validation
"""

from ast import dump
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, EXCLUDE

# ma initialized in app.py
ma = Marshmallow()


class HealthCheckSchema(ma.Schema):
    """Health check response schema"""

    search_engine = fields.Bool(dump_only=True, required=True)


class SuccessSchema(ma.Schema):
    """Generic success response schema"""

    success = fields.Bool(dump_only=True, required=True)


class DocumentBodySchema(ma.Schema):
    """Schema for document creation request"""

    body = fields.Str(required=True, validate=validate.Length(min=1))

    class Meta:
        unknown = EXCLUDE


class DocumentSchema(ma.Schema):
    """Schema for document response"""

    id = fields.Int(dump_only=True, required=True)
    title = fields.Str(dump_only=True, required=True, allow_none=True)
    outline = fields.Str(dump_only=True, required=True, allow_none=True)
    body = fields.Str(required=True)
    added_at = fields.DateTime(required=True)


class DocumentResponseSchema(ma.Schema):
    """Schema for single document response"""

    success = fields.Bool(dump_only=True, required=True)
    document = fields.Nested(DocumentSchema, dump_only=True, required=True)


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


class SearchResponseSchema(ma.Schema):
    """Schema for search results response"""

    success = fields.Bool(required=True)
    results = fields.List(fields.Nested(DocumentSchema), required=True)
    query = fields.Str(required=True)


class ImageSearchResultSchema(ma.Schema):
    """Schema for image search result"""

    # Adjust these fields based on what engine.search_images() returns
    url = fields.Str(dump_only=True, required=True)
    title = fields.Str(dump_only=True, allow_none=True)
    thumbnail = fields.Str(dump_only=True, allow_none=True)


class ImageSearchResponseSchema(ma.Schema):
    """Schema for image search results response"""

    success = fields.Bool(dump_only=True, required=True)
    results = fields.List(
        fields.Nested(ImageSearchResultSchema), dump_only=True, required=True
    )
    query = fields.Str(dump_only=True, required=True)


class ErrorSchema(ma.Schema):
    """Schema for error responses"""

    success = fields.Bool(dump_only=True, dump_default=False, required=True)
    error = fields.Int(dump_only=True, required=True)
    message = fields.Str(dump_only=True, required=True)
