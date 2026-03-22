"""
fast_errors — structured exceptions for FastMVC-style APIs.

Public API:
    - :class:`IError`
    - :class:`BadInputError`, :class:`NotFoundError`, :class:`UnexpectedResponseError`
    - :class:`UnauthorizedError`, :class:`ForbiddenError`, :class:`ConflictError`
    - :class:`RateLimitError`, :class:`ServiceUnavailableError`
"""

from .bad_input_error import BadInputError
from .conflict_error import ConflictError
from .error import IError
from .forbidden_error import ForbiddenError
from .not_found_error import NotFoundError
from .rate_limit_error import RateLimitError
from .service_unavailable_error import ServiceUnavailableError
from .unauthorized_error import UnauthorizedError
from .unexpected_response_error import UnexpectedResponseError

__all__ = [
    "IError",
    "BadInputError",
    "ConflictError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ServiceUnavailableError",
    "UnauthorizedError",
    "UnexpectedResponseError",
]
__version__ = "0.2.0"
