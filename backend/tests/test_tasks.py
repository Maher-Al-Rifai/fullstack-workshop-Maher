import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.models.task import TaskStatus  # noqa: E402
from app.services.task_transitions import validate_transition  # noqa: E402
from app.core.exceptions import InvalidTransitionError  # noqa: E402


# --- Pure transition rule unit tests (no HTTP, no DB) ---


def test_backlog_to_in_progress_allowed() -> None:
    validate_transition(TaskStatus.backlog, TaskStatus.in_progress)  # must not raise


def test_in_progress_to_done_allowed() -> None:
    validate_transition(TaskStatus.in_progress, TaskStatus.done)  # must not raise


def test_backlog_to_done_rejected() -> None:
    with pytest.raises(InvalidTransitionError):
        validate_transition(TaskStatus.backlog, TaskStatus.done)


def test_same_state_is_noop() -> None:
    validate_transition(TaskStatus.backlog, TaskStatus.backlog)  # must not raise


def test_backward_transition_rejected() -> None:
    with pytest.raises(InvalidTransitionError):
        validate_transition(TaskStatus.done, TaskStatus.backlog)


# --- HTTP integration tests ---


@pytest.fixture
def project_id(client: TestClient) -> int:
    r = client.post("/api/v1/projects", json={"name": "Task Project"})
    return r.json()["id"]


def test_create_task_returns_201_with_backlog_status(
    client: TestClient, project_id: int
) -> None:
    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "First task", "priority": "high"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "First task"
    assert data["status"] == "backlog"


def test_list_tasks_for_project(client: TestClient, project_id: int) -> None:
    client.post(f"/api/v1/projects/{project_id}/tasks", json={"title": "Task A"})
    client.post(f"/api/v1/projects/{project_id}/tasks", json={"title": "Task B"})

    response = client.get(f"/api/v1/projects/{project_id}/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_valid_two_step_transition(client: TestClient, project_id: int) -> None:
    r = client.post(
        f"/api/v1/projects/{project_id}/tasks", json={"title": "Transition task"}
    )
    task_id = r.json()["id"]

    r2 = client.patch(
        f"/api/v1/projects/{project_id}/tasks/{task_id}",
        json={"status": "in_progress"},
    )
    assert r2.json()["status"] == "in_progress"

    r3 = client.patch(
        f"/api/v1/projects/{project_id}/tasks/{task_id}",
        json={"status": "done"},
    )
    assert r3.json()["status"] == "done"


def test_invalid_direct_transition_returns_409(
    client: TestClient, project_id: int
) -> None:
    r = client.post(
        f"/api/v1/projects/{project_id}/tasks", json={"title": "Direct transition"}
    )
    task_id = r.json()["id"]

    response = client.patch(
        f"/api/v1/projects/{project_id}/tasks/{task_id}",
        json={"status": "done"},
    )

    assert response.status_code == 409
    assert response.json()["code"] == "conflict"


def test_task_not_found_through_wrong_project(
    client: TestClient, project_id: int
) -> None:
    r = client.post("/api/v1/projects", json={"name": "Other Project"})
    other_project_id = r.json()["id"]

    task_r = client.post(
        f"/api/v1/projects/{project_id}/tasks", json={"title": "Orphan task"}
    )
    task_id = task_r.json()["id"]

    response = client.patch(
        f"/api/v1/projects/{other_project_id}/tasks/{task_id}",
        json={"title": "Injected"},
    )

    assert response.status_code == 404


def test_delete_task_returns_204(client: TestClient, project_id: int) -> None:
    r = client.post(f"/api/v1/projects/{project_id}/tasks", json={"title": "Delete me"})
    task_id = r.json()["id"]

    response = client.delete(f"/api/v1/projects/{project_id}/tasks/{task_id}")

    assert response.status_code == 204
