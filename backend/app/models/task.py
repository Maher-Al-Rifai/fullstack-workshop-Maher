import enum
from datetime import date, datetime, timezone

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TaskStatus(str, enum.Enum):
    backlog = "backlog"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str]
    description: Mapped[str | None]
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.backlog)
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.medium)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimate_hours: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    project: Mapped["Project"] = relationship(  # type: ignore[name-defined]
        "Project", back_populates="tasks"
    )
