from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate, PublicProjectRead
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    return project_service.list_projects(db, current_user.id)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.create_project(db, current_user.id, data)


@router.get("/public/{slug}", response_model=PublicProjectRead)
def get_public_project(slug: str, db: Session = Depends(get_db)):
    try:
        return project_service.get_public_by_slug_with_counts(db, slug)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return project_service.get_visible_or_404(db, project_id, current_user.id)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return project_service.update_project(db, project_id, current_user.id, data)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    from app.repositories import project_repository

    project = project_repository.get_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    project_service.delete_project(db, project_id, current_user.id)
