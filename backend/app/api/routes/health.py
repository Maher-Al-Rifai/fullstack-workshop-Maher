from fastapi import APIRouter, HTTPException, status

from app.db.session import database_is_ready

router = APIRouter(tags=["health"])


@router.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "alive"}


@router.get("/health/ready")
def ready() -> dict[str, str]:
    try:
        ok = database_is_ready()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        )
    return {"status": "ready"}


@router.get("/health")
def health() -> dict[str, str]:
    try:
        database_is_ready()
        db_status = "ok"
    except Exception:
        db_status = "unavailable"
    return {"process": "alive", "database": db_status}
