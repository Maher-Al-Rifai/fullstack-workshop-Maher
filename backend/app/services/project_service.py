from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User


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
