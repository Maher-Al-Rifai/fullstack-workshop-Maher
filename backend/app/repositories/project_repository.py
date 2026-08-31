import re

from sqlalchemy.orm import Session

from app.models.project import Project


def _slugify(name: str) -> str:
    value = name.encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"[^a-z0-9-]", "", value)
    value = re.sub(r"-+", "-", value)
    value = value.strip("-")
    return value or "project"


def _unique_slug(db: Session, base: str) -> str:
    slug = base
    counter = 1
    while db.query(Project).filter(Project.slug == slug).first() is not None:
        slug = f"{base}-{counter}"
        counter += 1
    return slug


def get_by_id(db: Session, project_id: int) -> Project | None:
    return db.get(Project, project_id)


def get_by_slug(db: Session, slug: str) -> Project | None:
    return db.query(Project).filter(Project.slug == slug).first()


def list_visible(db: Session, user_id: int) -> list[Project]:
    return (
        db.query(Project)
        .filter((Project.owner_id == user_id) | (Project.is_public.is_(True)))
        .all()
    )


def add(db: Session, project: Project) -> None:
    db.add(project)


def create_with_slug(db: Session, project: Project) -> Project:
    base = _slugify(project.name)
    project.slug = _unique_slug(db, base)
    db.add(project)
    return project


def delete(db: Session, project: Project) -> None:
    db.delete(project)
