from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.project import Project
from app.repositories import project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_visible_or_404(db: Session, project_id: int, user_id: int) -> Project:
    project = project_repository.get_by_id(db, project_id)
    if project is None or (not project.is_public and project.owner_id != user_id):
        raise NotFoundError("Project not found")
    return project


def list_projects(db: Session, user_id: int) -> list[Project]:
    return project_repository.list_visible(db, user_id)


def create_project(db: Session, user_id: int, data: ProjectCreate) -> Project:
    project = Project(
        name=data.name,
        description=data.description,
        is_public=data.is_public,
        owner_id=user_id,
        slug="",  # assigned by repository
    )
    project_repository.create_with_slug(db, project)
    db.commit()
    db.refresh(project)
    return project


def update_project(
    db: Session, project_id: int, user_id: int, data: ProjectUpdate
) -> Project:
    project = get_visible_or_404(db, project_id, user_id)
    if data.name is not None:
        project.name = data.name
        base = project_repository._slugify(data.name)
        new_slug = project_repository._unique_slug(db, base)
        project.slug = new_slug
    if data.description is not None:
        project.description = data.description
    if data.is_public is not None:
        project.is_public = data.is_public
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, user_id: int) -> None:
    project = project_repository.get_by_id(db, project_id)
    if project is None:
        raise NotFoundError("Project not found")
    project_repository.delete(db, project)
    db.commit()


def get_public_by_slug(db: Session, slug: str) -> Project:
    project = project_repository.get_by_slug(db, slug)
    if project is None or not project.is_public:
        raise NotFoundError("Project not found")
    return project
