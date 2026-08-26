"""Unit tests for the task state-machine transition rules.

These tests have no HTTP, database, or FastAPI dependency — just pure logic.
"""

import pytest

from app.core.exceptions import InvalidTransitionError
from app.models.task import TaskStatus
from app.services.task_transitions import ALLOWED_TRANSITIONS, validate_transition

# ---------------------------------------------------------------------------
# Complete transition table — every (from, to) pair is explicit
# ---------------------------------------------------------------------------

_ALLOWED = [
    (TaskStatus.backlog, TaskStatus.in_progress),
    (TaskStatus.backlog, TaskStatus.cancelled),
    (TaskStatus.in_progress, TaskStatus.done),
    (TaskStatus.in_progress, TaskStatus.cancelled),
]

_REJECTED = [
    (TaskStatus.backlog, TaskStatus.done),
    (TaskStatus.done, TaskStatus.backlog),
    (TaskStatus.done, TaskStatus.in_progress),
    (TaskStatus.done, TaskStatus.cancelled),
    (TaskStatus.cancelled, TaskStatus.backlog),
    (TaskStatus.cancelled, TaskStatus.in_progress),
    (TaskStatus.cancelled, TaskStatus.done),
    (TaskStatus.in_progress, TaskStatus.backlog),
]

_NOOP = [
    (TaskStatus.backlog, TaskStatus.backlog),
    (TaskStatus.in_progress, TaskStatus.in_progress),
    (TaskStatus.done, TaskStatus.done),
    (TaskStatus.cancelled, TaskStatus.cancelled),
]


@pytest.mark.parametrize("current, next_status", _ALLOWED)
def test_allowed_transition_does_not_raise(
    current: TaskStatus, next_status: TaskStatus
) -> None:
    validate_transition(current, next_status)  # must not raise


@pytest.mark.parametrize("current, next_status", _REJECTED)
def test_rejected_transition_raises_invalid_transition(
    current: TaskStatus, next_status: TaskStatus
) -> None:
    with pytest.raises(InvalidTransitionError):
        validate_transition(current, next_status)


@pytest.mark.parametrize("status", list(TaskStatus))
def test_same_state_is_always_accepted(status: TaskStatus) -> None:
    validate_transition(status, status)  # must not raise


def test_allowed_transitions_dict_covers_all_statuses() -> None:
    """Every TaskStatus must have an entry so no status silently allows everything."""
    for status in TaskStatus:
        assert status in ALLOWED_TRANSITIONS, (
            f"{status} missing from ALLOWED_TRANSITIONS"
        )


def test_cancelled_is_a_terminal_state() -> None:
    assert ALLOWED_TRANSITIONS[TaskStatus.cancelled] == set()


def test_done_is_a_terminal_state() -> None:
    assert ALLOWED_TRANSITIONS[TaskStatus.done] == set()
