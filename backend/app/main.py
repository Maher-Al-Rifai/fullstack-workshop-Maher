from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import database_is_ready

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        {"detail": str(exc), "code": "conflict"},
        status_code=status.HTTP_409_CONFLICT,
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        {"detail": str(exc)},
        status_code=status.HTTP_404_NOT_FOUND,
    )


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


from app.api.routes.auth import router as auth_router  # noqa: E402
from app.api.routes.projects import router as projects_router  # noqa: E402
from app.api.routes.tasks import router as tasks_router  # noqa: E402

_API_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=_API_PREFIX)
app.include_router(projects_router, prefix=_API_PREFIX)
app.include_router(tasks_router, prefix=_API_PREFIX)
