import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")

import pytest  # noqa: E402
from datetime import datetime, timedelta, timezone  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import jwt  # noqa: E402

from app.core.tokens import create_refresh_token  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.repositories import user_repository  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _register(client: TestClient, email: str, password: str = "securepass123") -> dict:
    r = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Test User", "password": password},
    )
    return r


def _login(client: TestClient, email: str, password: str = "securepass123") -> dict:
    return client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_register_returns_201_without_password_fields(auth_client: TestClient) -> None:
    r = _register(auth_client, "new@example.com")

    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "new@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_password_is_stored_as_argon2_hash(auth_client: TestClient, db_session) -> None:
    _register(auth_client, "hashcheck@example.com", password="plaintext123")

    user = user_repository.get_by_email(db_session, "hashcheck@example.com")
    assert user is not None
    assert user.password_hash != "plaintext123"
    assert user.password_hash.startswith("$argon2")


def test_duplicate_registration_returns_409(auth_client: TestClient) -> None:
    body = {"email": "dup@example.com", "full_name": "Dup", "password": "password123"}
    auth_client.post("/api/v1/auth/register", json=body)

    r = auth_client.post("/api/v1/auth/register", json=body)

    assert r.status_code == 409
    assert r.json()["code"] == "conflict"


def test_email_is_normalised_to_lowercase(auth_client: TestClient, db_session) -> None:
    _register(auth_client, "UPPER@Example.COM")

    user = user_repository.get_by_email(db_session, "upper@example.com")
    assert user is not None


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


def test_login_returns_access_token_and_sets_httponly_cookie(
    auth_client: TestClient,
) -> None:
    _register(auth_client, "login@example.com")

    r = _login(auth_client, "login@example.com")

    assert r.status_code == 200
    assert "access_token" in r.json()
    assert r.json()["token_type"] == "bearer"
    assert "refresh_token" in r.cookies


def test_wrong_password_returns_generic_401(auth_client: TestClient) -> None:
    _register(auth_client, "wp@example.com", password="correctpass123")

    r = _login(auth_client, "wp@example.com", password="wrongpassword")

    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"


def test_unknown_email_returns_same_error_as_wrong_password(
    auth_client: TestClient,
) -> None:
    r = _login(auth_client, "nobody@example.com")

    # Must be identical so callers cannot enumerate registered emails
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"


# ---------------------------------------------------------------------------
# Protected endpoint (/me)
# ---------------------------------------------------------------------------


def test_me_without_token_returns_401(auth_client: TestClient) -> None:
    r = auth_client.get("/api/v1/auth/me")

    assert r.status_code == 401


def test_me_with_valid_token_returns_user(auth_client: TestClient) -> None:
    _register(auth_client, "me@example.com")
    login_r = _login(auth_client, "me@example.com")
    token = login_r.json()["access_token"]

    r = auth_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert r.status_code == 200
    assert r.json()["email"] == "me@example.com"


def test_invalid_token_returns_401(auth_client: TestClient) -> None:
    r = auth_client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer notavalidtoken"}
    )

    assert r.status_code == 401


def test_expired_token_returns_401(auth_client: TestClient) -> None:
    settings = get_settings()
    expired = jwt.encode(
        {
            "sub": "999",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
            "type": "access",
        },
        settings.secret_key,
        algorithm="HS256",
    )

    r = auth_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"}
    )

    assert r.status_code == 401


def test_token_with_no_sub_returns_401(auth_client: TestClient) -> None:
    settings = get_settings()
    no_sub_token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5), "type": "access"},
        settings.secret_key,
        algorithm="HS256",
    )

    r = auth_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {no_sub_token}"}
    )

    assert r.status_code == 401


def test_token_with_non_integer_sub_returns_401(auth_client: TestClient) -> None:
    settings = get_settings()
    bad_sub_token = jwt.encode(
        {
            "sub": "not-an-int",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "type": "access",
        },
        settings.secret_key,
        algorithm="HS256",
    )

    r = auth_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {bad_sub_token}"}
    )

    assert r.status_code == 401


def test_refresh_token_cannot_act_as_access_token(
    auth_client: TestClient, db_session
) -> None:
    _register(auth_client, "rt@example.com")
    user = user_repository.get_by_email(db_session, "rt@example.com")
    refresh = create_refresh_token(user.id)

    r = auth_client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh}"}
    )

    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Refresh endpoint
# ---------------------------------------------------------------------------


def test_refresh_issues_new_access_token(auth_client: TestClient) -> None:
    _register(auth_client, "ref@example.com")
    _login(auth_client, "ref@example.com")  # sets refresh_token cookie in client jar

    r = auth_client.post("/api/v1/auth/refresh")

    assert r.status_code == 200
    assert "access_token" in r.json()


def test_refresh_with_inactive_user_returns_401(
    auth_client: TestClient, db_session
) -> None:
    from app.repositories import user_repository

    _register(auth_client, "deact@example.com")
    user = user_repository.get_by_email(db_session, "deact@example.com")
    refresh_tok = create_refresh_token(user.id)
    user.is_active = False
    db_session.commit()

    r = auth_client.post("/api/v1/auth/refresh", cookies={"refresh_token": refresh_tok})

    assert r.status_code == 401


def test_refresh_without_cookie_returns_401(auth_client: TestClient) -> None:
    r = auth_client.post("/api/v1/auth/refresh", cookies={})

    assert r.status_code == 401


def test_logout_clears_cookie(auth_client: TestClient) -> None:
    _register(auth_client, "logout@example.com")
    _login(auth_client, "logout@example.com")

    r = auth_client.post("/api/v1/auth/logout")

    assert r.status_code == 204


# ---------------------------------------------------------------------------
# Cross-user resource isolation
# ---------------------------------------------------------------------------


@pytest.fixture
def _two_users(auth_client: TestClient):
    """Returns (owner_token, other_token, project_id)."""
    _register(auth_client, "owner2@example.com")
    _register(auth_client, "other2@example.com")

    owner_token = _login(auth_client, "owner2@example.com").json()["access_token"]
    other_token = _login(auth_client, "other2@example.com").json()["access_token"]

    r = auth_client.post(
        "/api/v1/projects",
        json={"name": "Private Project", "is_public": False},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    project_id = r.json()["id"]
    return owner_token, other_token, project_id


def test_other_user_cannot_read_private_project(
    auth_client: TestClient, _two_users
) -> None:
    _, other_token, project_id = _two_users

    r = auth_client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert r.status_code == 404


def test_other_user_cannot_update_private_project(
    auth_client: TestClient, _two_users
) -> None:
    _, other_token, project_id = _two_users

    r = auth_client.patch(
        f"/api/v1/projects/{project_id}",
        json={"name": "Hijacked"},
        headers={"Authorization": f"Bearer {other_token}"},
    )

    assert r.status_code == 404
