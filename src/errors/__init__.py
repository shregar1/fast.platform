"""
fast_errors — structured exceptions for FastMVC-style APIs.

Public API:
    - :class:`IError`
    - :class:`BadInputError`, :class:`NotFoundError`, :class:`UnexpectedResponseError`
    - :class:`UnauthorizedError`, :class:`ForbiddenError`, :class:`ConflictError`
    - :class:`RateLimitError`, :class:`ServiceUnavailableError`
"""

from fast_errors.bad_input_error import BadInputError
from fast_errors.conflict_error import ConflictError
from fast_errors.error import IError
from fast_errors.forbidden_error import ForbiddenError
from fast_errors.not_found_error import NotFoundError
from fast_errors.rate_limit_error import RateLimitError
from fast_errors.service_unavailable_error import ServiceUnavailableError
from fast_errors.unauthorized_error import UnauthorizedError
from fast_errors.unexpected_response_error import UnexpectedResponseError

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
