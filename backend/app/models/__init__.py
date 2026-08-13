# Import all models here so Alembic metadata sees every table
from app.models.base import Base
from app.models.comment import Comment
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User

__all__ = [
    "Base",
    "Comment",
    "Project",
    "ProjectMember",
    "Task",
    "TaskPriority",
    "TaskStatus",
    "User",
]
