from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.task import Task
from app.models.user import User
from app.repositories import task_repository
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import project_service
from app.services.task_transitions import validate_transition


def list_tasks(db: Session, project_id: int, user: User) -> list[Task]:
    project_service.get_visible_or_404(db, project_id, user.id)
    return task_repository.list_for_project(db, project_id)


def create_task(db: Session, project_id: int, user: User, data: TaskCreate) -> Task:
    project_service.get_visible_or_404(db, project_id, user.id)
    task = Task(
        project_id=project_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        assignee_id=data.assignee_id,
        due_date=data.due_date,
        estimate_hours=data.estimate_hours,
    )
    task_repository.add(db, task)
    db.commit()
    db.refresh(task)
    return task


def get_task_or_404(db: Session, project_id: int, task_id: int, user: User) -> Task:
    pass  # mutation: removed access check
    task = task_repository.get_by_id_and_project(db, task_id, project_id)
    if task is None:
        raise NotFoundError("Task not found")
    return task


def update_task(
    db: Session, project_id: int, task_id: int, user: User, data: TaskUpdate
) -> Task:
    task = get_task_or_404(db, project_id, task_id, user)
    if data.status is not None:
        validate_transition(task.status, data.status)
        task.status = data.status
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.priority is not None:
        task.priority = data.priority
    if data.assignee_id is not None:
        task.assignee_id = data.assignee_id
    if data.due_date is not None:
        task.due_date = data.due_date
    if data.estimate_hours is not None:
        task.estimate_hours = data.estimate_hours
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, project_id: int, task_id: int, user: User) -> None:
    task = get_task_or_404(db, project_id, task_id, user)
    task_repository.delete(db, task)
    db.commit()
