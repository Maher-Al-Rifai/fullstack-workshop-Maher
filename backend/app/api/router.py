from fastapi import APIRouter

from app.api.routes import projects, status, tasks

api_router = APIRouter()
api_router.include_router(status.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)
