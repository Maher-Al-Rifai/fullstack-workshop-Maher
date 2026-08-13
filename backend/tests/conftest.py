import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.api.deps import get_current_user, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.base import Base  # noqa: E402
from app.models.user import User  # noqa: E402

SQLITE_URL = "sqlite+pysqlite:///:memory:"
_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})


@event.listens_for(_engine, "connect")
def _fk_pragma(conn, _):
    conn.execute("PRAGMA foreign_keys=ON")


Base.metadata.create_all(_engine)
_Session = sessionmaker(bind=_engine)


@pytest.fixture(autouse=True)
def db_session():
    """Each test gets a fresh transaction rolled back after the test."""
    connection = _engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def owner(db_session: Session) -> User:
    user = User(
        email="owner@test.com",
        full_name="Test Owner",
        password_hash="x",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def other_user(db_session: Session) -> User:
    user = User(
        email="other@test.com",
        full_name="Other User",
        password_hash="x",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def client(db_session: Session, owner: User) -> TestClient:
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: owner
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def other_client(db_session: Session, other_user: User) -> TestClient:
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: other_user
    yield TestClient(app)
    app.dependency_overrides.clear()
