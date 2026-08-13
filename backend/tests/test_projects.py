import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient  # noqa: E402

from app.api.deps import get_current_user  # noqa: E402
from app.main import app  # noqa: E402


def test_create_project_returns_201(client: TestClient) -> None:
    response = client.post("/api/v1/projects", json={"name": "My Project"})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Project"
    assert "slug" in data
    assert "id" in data


def test_list_projects_returns_owned_projects(client: TestClient) -> None:
    client.post("/api/v1/projects", json={"name": "Project A"})
    client.post("/api/v1/projects", json={"name": "Project B"})

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_slug_collision_generates_unique_suffix(client: TestClient) -> None:
    r1 = client.post("/api/v1/projects", json={"name": "Duplicate"})
    r2 = client.post("/api/v1/projects", json={"name": "Duplicate"})

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["slug"] != r2.json()["slug"]


def test_private_project_not_visible_to_other_user(
    client: TestClient, other_user
) -> None:
    r = client.post("/api/v1/projects", json={"name": "Secret", "is_public": False})
    project_id = r.json()["id"]

    # Switch current user for this assertion only
    app.dependency_overrides[get_current_user] = lambda: other_user
    response = client.get(f"/api/v1/projects/{project_id}")

    assert response.status_code == 404


def test_public_project_visible_via_slug(client: TestClient) -> None:
    r = client.post(
        "/api/v1/projects", json={"name": "Open Project", "is_public": True}
    )
    slug = r.json()["slug"]

    response = client.get(f"/api/v1/projects/public/{slug}")

    assert response.status_code == 200
    assert response.json()["slug"] == slug
    assert "task_count" in response.json()


def test_update_project_name(client: TestClient) -> None:
    r = client.post("/api/v1/projects", json={"name": "Old Name"})
    project_id = r.json()["id"]

    response = client.patch(f"/api/v1/projects/{project_id}", json={"name": "New Name"})

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_other_user_cannot_update_project(client: TestClient, other_user) -> None:
    r = client.post(
        "/api/v1/projects", json={"name": "Owner Project", "is_public": True}
    )
    project_id = r.json()["id"]

    # Switch current user for this assertion only
    app.dependency_overrides[get_current_user] = lambda: other_user
    response = client.patch(f"/api/v1/projects/{project_id}", json={"name": "Hijacked"})

    assert response.status_code == 403


def test_delete_project_returns_204(client: TestClient) -> None:
    r = client.post("/api/v1/projects", json={"name": "To Delete"})
    project_id = r.json()["id"]

    response = client.delete(f"/api/v1/projects/{project_id}")

    assert response.status_code == 204
    assert client.get(f"/api/v1/projects/{project_id}").status_code == 404
