import pytest
from app.models import ApiKey, Document

@pytest.fixture
def sample_document(session):
    doc = Document(body="<html><body><p>Test content for search</p></body></html>")
    doc.insert()
    return doc

@pytest.fixture(autouse=True)
def enable_rate_limit(app):
    """Enable rate limiting for this module"""
    from app.extensions import limiter
    limiter.enabled = True
    yield
    limiter.enabled = False

def test_api_key_generation(client, db):
    response = client.post("/api/keys", json={"description": "Test Key"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "api_key" in data
    assert "key" in data["api_key"]
    assert data["api_key"]["description"] == "Test Key"

def test_rate_limiting_no_key(client, sample_document):
    # Hit the endpoint 11 times (limit is 10 per minute)
    for _ in range(10):
        response = client.get("/search?query=test")
        assert response.status_code == 200

    response = client.get("/search?query=test")
    assert response.status_code == 429

def test_rate_limiting_with_key(client, sample_document):
    response = client.post("/api/keys", json={"description": "Test Key"})
    api_key = response.get_json()["api_key"]["key"]

    headers = {"X-API-KEY": api_key}
    for _ in range(15):
        response = client.get("/search?query=test", headers=headers)
        assert response.status_code == 200
