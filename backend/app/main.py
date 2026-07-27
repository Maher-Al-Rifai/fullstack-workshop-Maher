from fastapi import FastAPI, HTTPException, status

from app.core.config import get_settings
from app.db.session import database_is_ready

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
def ready() -> dict[str, str]:
    try:
        ready_state = database_is_ready()
    except Exception as exc:  # database details belong in logs, not the response
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc

    if not ready_state:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        )
    return {"status": "ready"}
