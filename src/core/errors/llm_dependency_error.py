"""Missing optional Python packages for LLM providers (HTTP 503)."""

from __future__ import annotations

from .abstraction import IError


class LLMDependencyError(IError):
    """
    Raised when code paths require an optional dependency that is not installed
    (e.g. ``openai``, ``anthropic`` extras).
    """

    def __init__(
        self,
        *,
        provider: str,
        pip_extra: str,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__()
        self.provider = provider
        self.pip_extra = pip_extra
        self.responseMessage = (
            f"Optional dependency for provider {provider!r} is not installed; "
            f"install with: pip install {pip_extra}"
        )
        self.responseKey = "llm.missing_dependency"
        self.httpStatusCode = 503
        if cause is not None:
            self.__cause__ = cause
        Exception.__init__(self, self.responseMessage)
