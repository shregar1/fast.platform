"""Unknown or invalid LLM provider identifier (HTTP 400)."""

from __future__ import annotations

from .abstraction import IError


class UnsupportedLLMProviderError(IError):
    """Raised when a provider name is not supported by the requested API."""

    def __init__(
        self,
        provider: str,
        *,
        detail: str | None = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            provider: The provider parameter.
            detail: The detail parameter.
        """
        super().__init__()
        self.provider = provider
        self.responseMessage = detail or f"Unsupported LLM provider: {provider!r}"
        self.responseKey = "llm.unsupported_provider"
        self.httpStatusCode = 400
        Exception.__init__(self, self.responseMessage)
