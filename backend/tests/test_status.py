import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_status_returns_expected_shape() -> None:
    response = client.get("/api/v1/status")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "environment" in data


def test_status_does_not_leak_secrets() -> None:
    response = client.get("/api/v1/status")

    body = response.text
    assert "secret_key" not in body
    assert "database_url" not in body
    assert "changeme" not in body


def test_ping_returns_201_with_echo() -> None:
    response = client.post("/api/v1/ping", json={"message": "hello"})

    assert response.status_code == 201
    assert response.json() == {"echo": "hello"}


def test_ping_missing_field_returns_422() -> None:
    response = client.post("/api/v1/ping", json={})

    assert response.status_code == 422
