from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.repositories import project_repository
from app.schemas.project import ProjectCreate, ProjectUpdate


def create_project(db: Session, owner: User, data: ProjectCreate) -> Project:
    slug = project_repository.unique_slug(db, data.name)
    project = Project(
        name=data.name,
        slug=slug,
        description=data.description,
        is_public=data.is_public,
        owner_id=owner.id,
    )
    project_repository.add(db, project)
    db.flush()
    db.add(ProjectMember(project_id=project.id, user_id=owner.id, role="owner"))
    db.commit()
    db.refresh(project)
    return project


def list_visible(db: Session, user_id: int) -> list[Project]:
    return project_repository.get_visible_to_user(db, user_id)


def get_visible_or_404(db: Session, project_id: int, user_id: int) -> Project:
    project = project_repository.get_by_id(db, project_id)
    # Return 404 for both missing and inaccessible projects to avoid leaking existence
    if project is None:
        raise NotFoundError("Project not found")
    is_owner = project.owner_id == user_id
    is_member = any(m.user_id == user_id for m in project.members)
    if not (is_owner or is_member or project.is_public):
        raise NotFoundError("Project not found")
    return project


def update_project(
    db: Session, project_id: int, user_id: int, data: ProjectUpdate
) -> Project:
    project = get_visible_or_404(db, project_id, user_id)
    if project.owner_id != user_id:
        raise ForbiddenError("Only the project owner can update this project")
    if data.name is not None:
        new_slug = project_repository.unique_slug(db, data.name)
        project.name = data.name
        project.slug = new_slug
    if data.description is not None:
        project.description = data.description
    if data.is_public is not None:
        project.is_public = data.is_public
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, user_id: int) -> None:
    project = get_visible_or_404(db, project_id, user_id)
    if project.owner_id != user_id:
        raise ForbiddenError("Only the project owner can delete this project")
    project_repository.delete(db, project)
    db.commit()


def get_public_by_slug(db: Session, slug: str) -> dict:
    project = project_repository.get_public_by_slug(db, slug)
    if project is None:
        raise NotFoundError("Project not found")
    done_count = sum(1 for t in project.tasks if t.status.value == "done")
    return {
        "id": project.id,
        "name": project.name,
        "slug": project.slug,
        "description": project.description,
        "task_count": len(project.tasks),
        "done_count": done_count,
    }


def create_project_with_owner(
    db: Session,
    *,
    name: str,
    slug: str,
    owner: User,
    description: str | None = None,
    is_public: bool = False,
) -> Project:
    """Create a project and its owner membership atomically.

    Both rows are added in the same transaction. If anything fails after
    the project insert but before commit, neither row persists.
    """
    project = Project(
        name=name,
        slug=slug,
        description=description,
        is_public=is_public,
        owner_id=owner.id,
    )
    db.add(project)
    db.flush()  # assign project.id without committing

    membership = ProjectMember(
        project_id=project.id,
        user_id=owner.id,
        role="owner",
    )
    db.add(membership)
    db.commit()
    db.refresh(project)
    return project
