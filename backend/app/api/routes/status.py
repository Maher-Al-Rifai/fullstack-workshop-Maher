from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(tags=["status"])


class StatusResponse(BaseModel):
    name: str
    version: str
    environment: str


class PingRequest(BaseModel):
    message: str


class PingResponse(BaseModel):
    echo: str


@router.get("/status", response_model=StatusResponse)
def status_check() -> StatusResponse:
    settings = get_settings()
    # secret_key, database_url, and token settings are intentionally omitted
    return StatusResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )


@router.post("/ping", response_model=PingResponse, status_code=201)
def ping(body: PingRequest) -> PingResponse:
    return PingResponse(echo=body.message)
