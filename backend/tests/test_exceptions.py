import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

from fastapi.testclient import TestClient  # noqa: E402

from app.core.exceptions import (  # noqa: E402
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from app.main import app  # noqa: E402


def _make_client_with_route(exc: Exception) -> TestClient:
    """Return a TestClient for app with a single test route that raises exc."""

    @app.get(f"/test-exc/{type(exc).__name__.lower()}")
    def _raise() -> None:
        raise exc

    return TestClient(app, raise_server_exceptions=False)


def test_not_found_domain_error_returns_404() -> None:
    client = _make_client_with_route(NotFoundError("thing not found"))
    response = client.get("/test-exc/notfounderror")

    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_unauthorized_domain_error_returns_401() -> None:
    client = _make_client_with_route(UnauthorizedError("bad token"))
    response = client.get("/test-exc/unauthorizederror")

    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


def test_forbidden_domain_error_returns_403() -> None:
    client = _make_client_with_route(ForbiddenError("not your resource"))
    response = client.get("/test-exc/forbiddenerror")

    assert response.status_code == 403
    assert response.json()["code"] == "forbidden"


def test_conflict_domain_error_returns_409() -> None:
    client = _make_client_with_route(ConflictError("already exists"))
    response = client.get("/test-exc/conflicterror")

    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
