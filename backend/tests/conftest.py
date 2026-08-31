import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

_TEST_DB_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(
        _TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture
def auth_client(db_session: Session):
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(db_session: Session):
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    c = TestClient(app)

    c.post(
        "/api/v1/auth/register",
        json={
            "email": "tester@example.com",
            "full_name": "Test User",
            "password": "testpassword123",
        },
    )
    r = c.post(
        "/api/v1/auth/login",
        json={"email": "tester@example.com", "password": "testpassword123"},
    )
    c.headers = {**c.headers, "Authorization": f"Bearer {r.json()['access_token']}"}

    yield c
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop("get_current_user", None)


@pytest.fixture
def other_user(db_session: Session):
    import argon2

    from app.models.user import User
    from app.repositories import user_repository

    ph = argon2.PasswordHasher()
    user = User(
        email="other@example.com",
        full_name="Other User",
        password_hash=ph.hash("otherpassword123"),
        is_active=True,
    )
    user_repository.add(db_session, user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(autouse=True)
def _clear_dependency_overrides():
    """Ensure dependency overrides are clean after each test."""
    yield
    from app.api.deps import get_current_user

    app.dependency_overrides.pop(get_current_user, None)
