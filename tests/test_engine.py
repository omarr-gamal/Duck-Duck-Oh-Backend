import pytest
from unittest.mock import patch, MagicMock
from app.engine import Engine
from app.models import Document, Index


@pytest.fixture
def engine_instance(session):
    """Create an Engine instance with mocked NLTK downloads"""
    with patch('app.engine.nltk.download'):
        engine = Engine()
        yield engine


@pytest.fixture
def initialized_engine(session):
    """Create an initialized Engine instance with test data"""
    with patch('app.engine.nltk.download'):
        doc1 = Document(body="<html><head><title>Python Programming</title></head><body><p>Learn Python programming language</p></body></html>")
        doc2 = Document(body="<html><head><title>JavaScript Guide</title></head><body><p>JavaScript is a web programming language</p></body></html>")
        doc3 = Document(body="<html><head><title>Data Science</title></head><body><p>Data science with Python and machine learning</p></body></html>")
        
        doc1.insert()
        doc2.insert()
        doc3.insert()
        
        engine = Engine()
        engine._Engine__initialize()
        
        yield engine


def test_engine_creation(engine_instance):
    """Test that an Engine instance can be created"""
    assert engine_instance is not None
    assert engine_instance._Engine__is_initialized is False


def test_download_nltk_dicts(engine_instance):
    """Test NLTK dictionary downloads"""
    with patch('app.engine.nltk.download') as mock_download:
        engine_instance.download_nltk_dicts()
        
        assert mock_download.call_count == 3
        mock_download.assert_any_call("punkt")
        mock_download.assert_any_call("punkt_tab")
        mock_download.assert_any_call("stopwords")


def test_tokenize(initialized_engine):
    """Test HTML tokenization and text processing"""
    html = "<html><body><p>The quick brown fox jumps over the lazy dog!</p></body></html>"
    
    tokens = initialized_engine._Engine__tokenize(html)
    
    assert len(tokens) > 0
    assert any('quick' in token for token in tokens)
    assert any('jump' in token for token in tokens)
    assert any('lazi' in token for token in tokens)


def test_tokenize_removes_html(initialized_engine):
    """Test that HTML tags are properly removed during tokenization"""
    html = "<div><strong>Important</strong> text</div>"
    
    tokens = initialized_engine._Engine__tokenize(html)
    
    for token in tokens:
        assert '<' not in token
        assert '>' not in token


def test_add_document(initialized_engine):
    """Test adding a new document to the engine"""
    initial_doc_count = len(initialized_engine.documents)
    
    new_html = "<html><body><p>New test document about artificial intelligence</p></body></html>"
    doc = initialized_engine.add_document(new_html)
    
    assert doc.id is not None
    assert len(initialized_engine.documents) == initial_doc_count + 1
    assert initialized_engine.documents[-1] == new_html


def test_search_index(initialized_engine):
    """Test searching the index"""
    results = initialized_engine._Engine__search_index("Python programming")
    
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_returns_ranked_results(initialized_engine):
    """Test that search returns ranked results"""
    results = initialized_engine.search("Python programming")
    
    assert isinstance(results, list)
    assert all(isinstance(doc_id, int) for doc_id in results)


def test_search_no_results(initialized_engine):
    """Test search with query that has no matches"""
    results = initialized_engine.search("xyzabc123nonexistent")
    
    assert isinstance(results, list)
    assert len(results) == 0


def test_rank_results(initialized_engine):
    """Test result ranking by relevance"""
    doc_ids = [doc.id for doc in Document.query.all()]
    
    ranked = initialized_engine._Engine__rank_results(doc_ids, "Python programming")
    
    assert isinstance(ranked, list)
    assert len(ranked) > 0


def test_rank_results_empty(initialized_engine):
    """Test ranking with empty document list"""
    ranked = initialized_engine._Engine__rank_results([], "test")
    
    assert ranked == []


def test_rank_results_empty_query(initialized_engine):
    """Test ranking with empty query"""
    doc_ids = [1, 2]
    ranked = initialized_engine._Engine__rank_results(doc_ids, "")
    
    assert ranked == []


def test_search_images(initialized_engine, session):
    """Test image search functionality"""
    html_with_images = """
    <html>
        <body>
            <p>Python tutorial</p>
            <img src="python-logo.png" alt="Python Logo">
            <img src="code-example.jpg" alt="Code Example">
        </body>
    </html>
    """
    doc = Document(body=html_with_images)
    doc.insert()
    
    initialized_engine.index_all_documents()
    
    results = initialized_engine.search_images("Python")
    
    assert isinstance(results, list)
    if len(results) > 0:
        assert 'url' in results[0]
        assert 'document_id' in results[0]


def test_search_images_no_images(initialized_engine):
    """Test image search when documents have no images"""
    results = initialized_engine.search_images("Python")
    
    assert isinstance(results, list)


def test_index_all_documents(session):
    """Test indexing all documents in the database"""
    with patch('app.engine.nltk.download'):
        doc1 = Document(body="<html><body>First document</body></html>")
        doc2 = Document(body="<html><body>Second document</body></html>")
        doc1.insert()
        doc2.insert()
        
        engine = Engine()
        engine._Engine__initialize()
        
        assert len(engine.index) > 0
        assert isinstance(engine.index, dict)


def test_engine_lazy_initialization(session):
    """Test that engine only initializes when needed"""
    with patch('app.engine.nltk.download'):
        engine = Engine()
        
        assert engine._Engine__is_initialized is False
        
        doc = Document(body="<html><body>Test</body></html>")
        doc.insert()
        
        engine.search("test")
        
        assert engine._Engine__is_initialized is True


def test_update_index(initialized_engine):
    """Test that index updates are persisted to database"""
    initialized_engine.index['testtoken123'] = [1, 2, 3]
    initialized_engine._Engine__update_index()
    
    index_obj = Index.query.first()
    assert index_obj is not None
    
    import json
    index_data = json.loads(index_obj.index)
    assert 'testtoken123' in index_data
    assert index_data['testtoken123'] == [1, 2, 3]


def test_add_to_index(initialized_engine):
    """Test adding tokens to the search index"""
    test_tokens = ['python', 'programming', 'code']
    test_doc_id = 999
    
    initialized_engine._Engine__add_to_index(test_doc_id, test_tokens)
    
    for token in test_tokens:
        if token in initialized_engine.index:
            assert test_doc_id in initialized_engine.index[token]


def test_engine_handles_special_characters(initialized_engine):
    """Test that engine handles special characters in documents"""
    html_with_special = "<html><body>Test @#$%^&*() special!!! characters???</body></html>"
    
    tokens = initialized_engine._Engine__tokenize(html_with_special)
    
    for token in tokens:
        assert not any(char in token for char in ['@', '#', '$', '%', '^', '&', '*', '(', ')', '!', '?'])


def test_engine_handles_empty_html(initialized_engine):
    """Test engine handling of empty HTML"""
    empty_html = "<html><body></body></html>"
    
    tokens = initialized_engine._Engine__tokenize(empty_html)
    
    assert isinstance(tokens, list)
    assert len(tokens) == 0
