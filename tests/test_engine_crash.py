import pytest
from app.models import Index
from app.engine import engine
import json

def test_engine_initialization_empty_index(session):
    # Manually insert an index with empty string
    ind = Index("")
    session.add(ind)
    session.commit()
    
    try:
        engine.search("test")
    except json.decoder.JSONDecodeError:
        pytest.fail("Engine failed to handle empty index")
