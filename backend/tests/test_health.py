import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_live_health_does_not_require_database() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_combined_health_returns_process_and_database_keys() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "process" in data
    assert "database" in data
