class WorkboardError(Exception):
    """Base class for all domain errors."""


class NotFoundError(WorkboardError):
    """Resource does not exist or is not visible to the caller."""


class UnauthorizedError(WorkboardError):
    """Authentication is missing or invalid."""


class ForbiddenError(WorkboardError):
    """Identity is known but lacks permission for this resource."""


class ConflictError(WorkboardError):
    """Request conflicts with current state (duplicate, invalid transition)."""


class InvalidTransitionError(ConflictError):
    """A state-machine transition is not allowed from the current state."""
