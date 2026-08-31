from sqlalchemy.orm import Session

from app.models.task import Task


def list_for_project(db: Session, project_id: int) -> list[Task]:
    return db.query(Task).filter(Task.project_id == project_id).all()


def get_by_id_and_project(db: Session, task_id: int, project_id: int) -> Task | None:
    return (
        db.query(Task)
        .filter(Task.id == task_id, Task.project_id == project_id)
        .first()
    )


def add(db: Session, task: Task) -> None:
    db.add(task)


def delete(db: Session, task: Task) -> None:
    db.delete(task)
