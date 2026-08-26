"""Integration tests for validation errors and edge-case branches.

These close branch-coverage gaps not covered by the primary test files.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")

from fastapi.testclient import TestClient  # noqa: E402


# ---------------------------------------------------------------------------
# Request validation (422 Unprocessable Entity)
# ---------------------------------------------------------------------------


def test_project_create_empty_name_returns_422(client: TestClient) -> None:
    r = client.post("/api/v1/projects", json={"name": ""})
    assert r.status_code == 422


def test_project_create_missing_name_returns_422(client: TestClient) -> None:
    r = client.post("/api/v1/projects", json={})
    assert r.status_code == 422


def test_task_create_empty_title_returns_422(client: TestClient) -> None:
    proj = client.post("/api/v1/projects", json={"name": "Proj"}).json()
    r = client.post(f"/api/v1/projects/{proj['id']}/tasks", json={"title": ""})
    assert r.status_code == 422


def test_register_short_password_returns_422(auth_client: TestClient) -> None:
    r = auth_client.post(
        "/api/v1/auth/register",
        json={"email": "x@x.com", "full_name": "X", "password": "short"},
    )
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Inactive user cannot access protected routes
# ---------------------------------------------------------------------------


def test_inactive_user_is_rejected_by_get_current_user(
    auth_client: TestClient, db_session
) -> None:
    from app.repositories import user_repository

    auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "inactive@example.com",
            "full_name": "I",
            "password": "pass1234",
        },
    )
    login_r = auth_client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "pass1234"},
    )
    token = login_r.json()["access_token"]

    # Deactivate the user directly in the DB
    user = user_repository.get_by_email(db_session, "inactive@example.com")
    user.is_active = False
    db_session.commit()

    r = auth_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Not-found behavior
# ---------------------------------------------------------------------------


def test_get_nonexistent_project_returns_404(client: TestClient) -> None:
    r = client.get("/api/v1/projects/99999")
    assert r.status_code == 404


def test_patch_nonexistent_task_returns_404(client: TestClient) -> None:
    proj = client.post("/api/v1/projects", json={"name": "P"}).json()
    r = client.patch(f"/api/v1/projects/{proj['id']}/tasks/99999", json={"title": "X"})
    assert r.status_code == 404


def test_public_slug_not_found_returns_404(client: TestClient) -> None:
    r = client.get("/api/v1/projects/public/does-not-exist")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Conflict behavior
# ---------------------------------------------------------------------------


def test_login_inactive_user_returns_401_with_generic_message(
    auth_client: TestClient, db_session
) -> None:
    from app.repositories import user_repository

    auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "disabled@example.com",
            "full_name": "D",
            "password": "pass1234",
        },
    )
    user = user_repository.get_by_email(db_session, "disabled@example.com")
    user.is_active = False
    db_session.commit()

    r = auth_client.post(
        "/api/v1/auth/login",
        json={"email": "disabled@example.com", "password": "pass1234"},
    )
    assert r.status_code == 401
    # Same generic message — no information about whether the account is disabled
    assert r.json()["detail"] == "Invalid credentials"


# ---------------------------------------------------------------------------
# Persistence side effects
# ---------------------------------------------------------------------------


def test_delete_project_removes_tasks_cascade(client: TestClient) -> None:
    proj = client.post("/api/v1/projects", json={"name": "CascadeP"}).json()
    client.post(f"/api/v1/projects/{proj['id']}/tasks", json={"title": "T1"})
    client.post(f"/api/v1/projects/{proj['id']}/tasks", json={"title": "T2"})

    client.delete(f"/api/v1/projects/{proj['id']}")

    # Project gone → tasks gone → 404
    r = client.get(f"/api/v1/projects/{proj['id']}/tasks")
    assert r.status_code == 404


def test_update_project_without_name_keeps_original_slug(client: TestClient) -> None:
    proj = client.post("/api/v1/projects", json={"name": "Original Name"}).json()
    original_slug = proj["slug"]

    updated = client.patch(
        f"/api/v1/projects/{proj['id']}", json={"description": "New desc"}
    ).json()

    assert updated["slug"] == original_slug


def test_update_project_visibility(client: TestClient) -> None:
    proj = client.post("/api/v1/projects", json={"name": "Vis Test"}).json()

    updated = client.patch(
        f"/api/v1/projects/{proj['id']}", json={"is_public": True}
    ).json()

    assert updated["is_public"] is True


def test_update_task_multiple_fields(client: TestClient) -> None:
    proj = client.post("/api/v1/projects", json={"name": "Task Fields"}).json()
    task = client.post(
        f"/api/v1/projects/{proj['id']}/tasks", json={"title": "T"}
    ).json()

    updated = client.patch(
        f"/api/v1/projects/{proj['id']}/tasks/{task['id']}",
        json={
            "description": "new desc",
            "priority": "high",
            "estimate_hours": 3,
            "due_date": "2027-01-15",
        },
    ).json()

    assert updated["description"] == "new desc"
    assert updated["priority"] == "high"
    assert updated["estimate_hours"] == 3
    assert updated["due_date"] == "2027-01-15"


def test_non_owner_cannot_delete_project(client: TestClient, other_user) -> None:
    from app.api.deps import get_current_user
    from app.main import app

    proj = client.post(
        "/api/v1/projects", json={"name": "Delete Test", "is_public": True}
    ).json()

    app.dependency_overrides[get_current_user] = lambda: other_user
    r = client.delete(f"/api/v1/projects/{proj['id']}")

    assert r.status_code == 403
