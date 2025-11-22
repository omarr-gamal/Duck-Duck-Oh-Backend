from unittest.mock import patch

def test_health_check(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"search_engine": True}

def test_create_document(client, session):
    html_body = "<html><head><title>Test Doc</title></head><body><p>Content</p></body></html>"
    
    with patch('app.main.routes.engine') as mock_engine:
        mock_engine.add_document.return_value = {"id": 1, "title": "Test Doc"}
        
        response = client.post('/documents', json={"body": html_body})
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['document'] == {"id": 1, "title": "Test Doc"}
        mock_engine.add_document.assert_called_once_with(html_body)

def test_get_document(client, session):
    from app.models import Document
    doc = Document(body="<html><head><title>Get Doc</title></head><body><p>Content</p></body></html>")
    doc.insert()
    
    response = client.get(f'/documents/{doc.id}')
    
    assert response.status_code == 200
    assert response.json['success'] is True
    assert response.json['document']['title'] == "Get Doc"

def test_get_document_not_found(client):
    response = client.get('/documents/999')
    assert response.status_code == 404

def test_search_documents(client, session):
    with patch('app.main.routes.engine') as mock_engine:
        from app.models import Document
        doc = Document(body="<html><head><title>Search Doc</title></head><body><p>Content</p></body></html>")
        session.add(doc)
        session.commit()
        
        mock_engine.search.return_value = [doc.id]
        
        response = client.get('/search?query=test')
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert len(response.json['results']) == 1
        assert response.json['results'][0]['title'] == "Search Doc"
        assert response.json['query'] == "test"

def test_search_images(client):
    with patch('app.main.routes.engine') as mock_engine:
        mock_engine.search_images.return_value = [
            {"url": "image1.jpg", "title": "Image 1", "thumbnail": "thumb1.jpg"},
            {"url": "image2.jpg", "title": "Image 2", "thumbnail": "thumb2.jpg"}
        ]
        
        response = client.get('/search/images?query=test')
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert len(response.json['results']) == 2
        assert response.json['results'][0]['url'] == "image1.jpg"
