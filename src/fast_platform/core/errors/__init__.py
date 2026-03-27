"""fast_errors — structured exceptions for FastMVC-style APIs.

Public API:
    - :class:`IError`
    - :class:`BadInputError`, :class:`NotFoundError`, :class:`UnexpectedResponseError`
    - :class:`UnauthorizedError`, :class:`ForbiddenError`, :class:`ConflictError`
    - :class:`RateLimitError`, :class:`ServiceUnavailableError`
    - :class:`LLMDependencyError`, :class:`UnsupportedLLMProviderError`, :class:`LLMFeatureNotAvailableError`
    - :class:`TokenBudgetExceeded`, :class:`CryptoConfigurationError`
"""

from .abstraction import IError
from .badinputerror import BadInputError
from .conflicterror import ConflictError
from .cryptoconfigurationerror import CryptoConfigurationError
from .forbiddenerror import ForbiddenError
from .llmdependencyerror import LLMDependencyError
from .llmfeaturenotavailableerror import LLMFeatureNotAvailableError
from .notfounderror import NotFoundError
from .ratelimiterror import RateLimitError
from .serviceunavailableerror import ServiceUnavailableError
from .tokenbudgetexceedederror import TokenBudgetExceeded
from .unauthorizederror import UnauthorizedError
from .unexpectedresponseerror import UnexpectedResponseError
from .unsupportedllmprovidererror import UnsupportedLLMProviderError

__all__ = [
    "IError",
    "BadInputError",
    "ConflictError",
    "CryptoConfigurationError",
    "ForbiddenError",
    "LLMDependencyError",
    "LLMFeatureNotAvailableError",
    "NotFoundError",
    "RateLimitError",
    "ServiceUnavailableError",
    "TokenBudgetExceeded",
    "UnauthorizedError",
    "UnexpectedResponseError",
    "UnsupportedLLMProviderError",
]
__version__ = "0.2.0"
