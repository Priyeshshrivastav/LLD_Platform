class NotFoundError(Exception):
    """Raised when a requested entity does not exist."""


class ValidationError(Exception):
    """Raised for client-input problems (e.g. incomplete submission)."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


class ConflictError(Exception):
    """Raised when an action is invalid given the entity's current state
    (e.g. submitting an already-submitted attempt, retrying a non-failed
    evaluation)."""
