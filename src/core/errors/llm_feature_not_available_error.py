"""LLM capability not implemented or not wired (HTTP 501)."""

from __future__ import annotations

from .abstraction import IError


class LLMFeatureNotAvailableError(IError):
    """Raised when a valid provider is used in a context that is not implemented yet."""

    def __init__(
        self,
        responseMessage: str,
        *,
        responseKey: str = "llm.feature_not_available",
        httpStatusCode: int = 501,
    ) -> None:
        """Execute __init__ operation.

        Args:
            responseMessage: The responseMessage parameter.
            responseKey: The responseKey parameter.
            httpStatusCode: The httpStatusCode parameter.
        """
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
        Exception.__init__(self, self.responseMessage)
