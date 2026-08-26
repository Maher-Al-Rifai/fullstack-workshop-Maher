from app.core.exceptions import InvalidTransitionError
from app.models.task import TaskStatus

# Pure function — no database, no side effects, fully unit-testable
ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.backlog: {TaskStatus.in_progress, TaskStatus.cancelled},
    TaskStatus.in_progress: {TaskStatus.done, TaskStatus.cancelled},
    TaskStatus.done: set(),
    TaskStatus.cancelled: set(),
}


def validate_transition(current: TaskStatus, next_status: TaskStatus) -> None:
    """Raise InvalidTransitionError if the status change is not allowed."""
    if next_status == current:
        return  # same-state update is a no-op
    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if next_status not in allowed:
        raise InvalidTransitionError(
            f"Cannot transition from '{current.value}' to '{next_status.value}'"
        )
