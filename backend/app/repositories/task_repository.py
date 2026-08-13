from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task import Task


def get_by_id_and_project(db: Session, task_id: int, project_id: int) -> Task | None:
    return db.scalar(
        select(Task).where(Task.id == task_id, Task.project_id == project_id)
    )


def list_for_project(db: Session, project_id: int) -> list[Task]:
    return list(db.scalars(select(Task).where(Task.project_id == project_id)))


def add(db: Session, task: Task) -> Task:
    db.add(task)
    return task


def delete(db: Session, task: Task) -> None:
    db.delete(task)
