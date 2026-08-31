from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium
    assignee_id: int | None = None
    due_date: date | None = None
    estimate_hours: float | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None
    due_date: date | None = None
    estimate_hours: float | None = None


class TaskRead(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee_id: int | None
    due_date: date | None
    estimate_hours: float | None
    created_at: datetime

    model_config = {"from_attributes": True}
