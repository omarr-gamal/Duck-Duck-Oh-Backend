import pytest
import os
from unittest.mock import patch
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    app = create_app('test_config.py')

    return app

@pytest.fixture(scope='session')
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()

@pytest.fixture(scope='function')
def session(db):
    session = db.session
    
    transaction = session.begin_nested()

    original_commit = session.commit
    session.commit = session.flush

    yield session

    session.commit = original_commit
    transaction.rollback()
    session.remove()

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

@pytest.fixture(scope='module')
def runner(app):
    return app.test_cli_runner()
