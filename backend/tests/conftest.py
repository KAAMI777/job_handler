import os

# A throwaway in-memory database so importing the app never needs a real Postgres.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app

_PG_URL = os.environ["DATABASE_URL"]
_HAS_PG = _PG_URL.startswith(("postgresql", "postgres"))

requires_db = pytest.mark.skipif(
    not _HAS_PG, reason="needs a Postgres DATABASE_URL (enum/JSONB types)"
)


@pytest.fixture
def client() -> TestClient:
    """Client with no database override — for tests that stub the DB themselves."""
    return TestClient(app)


@pytest.fixture(scope="session")
def _engine():
    if not _HAS_PG:
        pytest.skip("needs a Postgres DATABASE_URL")
    from alembic import command
    from alembic.config import Config

    engine = create_engine(_PG_URL)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    # Build the schema the same way production does, so tests exercise the migrations.
    command.upgrade(Config("alembic.ini"), "head")
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(_engine):
    """A session wrapped in a transaction that is rolled back after each test."""
    connection = _engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection, autoflush=False)()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def api_client(db_session) -> TestClient:
    """Client whose request handlers use the rolled-back test session."""
    from app.db.session import get_db

    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()
