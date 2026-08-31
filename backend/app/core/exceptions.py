class AppError(Exception):
    """Base for all application-layer errors."""


class UnauthorizedError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass


class InvalidTransitionError(AppError):
    pass
