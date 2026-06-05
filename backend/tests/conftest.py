"""
Pytest configuration — shared fixtures for all test modules.
"""
import pytest
from app import create_app
from app.config.settings import TestingConfig
from app.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """Create an app instance configured for testing."""
    application = create_app(TestingConfig)
    yield application


@pytest.fixture(scope='session')
def db(app):
    """Create all tables in the in-memory test database."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app, db):
    """Provide a test client with a clean DB state for each test."""
    with app.test_client() as client:
        with app.app_context():
            yield client
            _db.session.rollback()
            for table in reversed(_db.metadata.sorted_tables):
                _db.session.execute(table.delete())
            _db.session.commit()
