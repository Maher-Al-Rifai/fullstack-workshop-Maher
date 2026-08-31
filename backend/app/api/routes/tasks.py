from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.exceptions import InvalidTransitionError, NotFoundError
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskRead])
def list_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    try:
        return task_service.list_tasks(db, project_id, current_user)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.create_task(db, project_id, current_user, data)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    project_id: int,
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.update_task(db, project_id, task_id, current_user, data)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except InvalidTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": str(exc), "code": "invalid_transition"},
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    try:
        task_service.delete_task(db, project_id, task_id, current_user)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
