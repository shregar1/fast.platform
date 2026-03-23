"""
fast_errors — structured exceptions for FastMVC-style APIs.

Public API:
    - :class:`IError`
    - :class:`BadInputError`, :class:`NotFoundError`, :class:`UnexpectedResponseError`
    - :class:`UnauthorizedError`, :class:`ForbiddenError`, :class:`ConflictError`
    - :class:`RateLimitError`, :class:`ServiceUnavailableError`
    - :class:`LLMDependencyError`, :class:`UnsupportedLLMProviderError`, :class:`LLMFeatureNotAvailableError`
    - :class:`TokenBudgetExceeded`, :class:`CryptoConfigurationError`
"""

from .abstraction import IError
from .bad_input_error import BadInputError
from .conflict_error import ConflictError
from .crypto_configuration_error import CryptoConfigurationError
from .forbidden_error import ForbiddenError
from .llm_dependency_error import LLMDependencyError
from .llm_feature_not_available_error import LLMFeatureNotAvailableError
from .not_found_error import NotFoundError
from .rate_limit_error import RateLimitError
from .service_unavailable_error import ServiceUnavailableError
from .token_budget_exceeded_error import TokenBudgetExceeded
from .unauthorized_error import UnauthorizedError
from .unexpected_response_error import UnexpectedResponseError
from .unsupported_llm_provider_error import UnsupportedLLMProviderError

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
