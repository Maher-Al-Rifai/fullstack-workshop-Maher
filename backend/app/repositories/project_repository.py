import re

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_member import ProjectMember


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "project"


def slug_exists(db: Session, slug: str) -> bool:
    return db.scalar(select(Project.id).where(Project.slug == slug)) is not None


def unique_slug(db: Session, name: str) -> str:
    base = _slugify(name)
    slug = base
    counter = 1
    while slug_exists(db, slug):
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def get_by_id(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def get_visible_to_user(db: Session, user_id: int) -> list[Project]:
    stmt = (
        select(Project)
        .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
        .where(
            or_(
                Project.owner_id == user_id,
                ProjectMember.user_id == user_id,
            )
        )
        .distinct()
    )
    return list(db.scalars(stmt))


def get_public_by_slug(db: Session, slug: str) -> Project | None:
    return db.scalar(
        select(Project).where(Project.slug == slug, Project.is_public.is_(True))
    )


def add(db: Session, project: Project) -> Project:
    db.add(project)
    return project


def delete(db: Session, project: Project) -> None:
    db.delete(project)
