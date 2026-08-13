import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from app.models.base import Base  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.project_member import ProjectMember  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.project_service import create_project_with_owner  # noqa: E402

# SQLite needs this pragma to enforce foreign keys
SQLITE_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture
def db() -> Session:
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def owner(db: Session) -> User:
    user = User(
        email="owner@example.com",
        full_name="Test Owner",
        password_hash="hashed",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_project_with_owner_inserts_both_rows(db: Session, owner: User) -> None:
    project = create_project_with_owner(
        db, name="My Project", slug="my-project", owner=owner
    )

    assert project.id is not None
    assert db.query(Project).count() == 1
    assert (
        db.query(ProjectMember).filter_by(user_id=owner.id, role="owner").count() == 1
    )


def test_rollback_prevents_partial_writes(db: Session, owner: User) -> None:
    """Simulate a failure after project insert but before membership commit."""

    try:
        project = Project(
            name="Partial Project",
            slug="partial-project",
            owner_id=owner.id,
        )
        db.add(project)
        db.flush()  # project gets an id but transaction is not committed

        # Simulated failure — membership not added
        raise RuntimeError("simulated failure mid-transaction")

    except RuntimeError:
        db.rollback()

    # Neither the project nor the membership should exist
    assert db.query(Project).count() == 0
    assert db.query(ProjectMember).count() == 0
