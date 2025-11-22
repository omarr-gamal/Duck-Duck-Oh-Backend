from app.models import Document, Index

def test_document_creation(session):
    html_body = "<html><head><title>Test Title</title></head><body><p>Test Outline</p></body></html>"
    doc = Document(body=html_body)
    
    assert doc.title == "Test Title"
    assert doc.outline == "Test Outline"
    assert doc.body == html_body
    
    doc.insert()
    assert doc.id is not None

def test_document_creation_no_title(session):
    html_body = "<html><body><p>Test Outline</p></body></html>"
    doc = Document(body=html_body)
    
    assert doc.title == ""
    assert doc.outline == "Test Outline"

def test_document_creation_div_outline(session):
    html_body = "<html><body><div>Test Outline Div</div></body></html>"
    doc = Document(body=html_body)
    
    assert doc.outline == "Test Outline Div"

def test_index_creation(session):
    idx = Index(index="test_index")
    idx.insert()
    
    assert idx.id is not None
    assert idx.index == "test_index"

def test_model_update(session):
    idx = Index(index="test_index")
    idx.insert()
    
    idx.index = "updated_index"
    idx.update()
    
    fetched_idx = session.get(Index, idx.id)
    assert fetched_idx.index == "updated_index"

def test_model_delete(session):
    idx = Index(index="test_index")
    idx.insert()
    
    idx_id = idx.id
    idx.delete()
    
    fetched_idx = session.get(Index, idx_id)
    assert fetched_idx is None
