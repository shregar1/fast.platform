"""Fast Platform — consolidated entry points for core platform services."""

from .core.errors import (
    BadInputError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    UnexpectedResponseError,
    RateLimitError,
    ServiceUnavailableError,
)

# If utils or other common aliases are needed, they can be added here.
