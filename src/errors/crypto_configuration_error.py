"""Invalid crypto service construction or environment (HTTP 400 / 503)."""

from __future__ import annotations

from .abstraction import IError


class CryptoConfigurationError(IError):
    """Raised when :class:`~service.crypto.CryptoService` parameters are invalid."""

    def __init__(
        self,
        responseMessage: str,
        *,
        responseKey: str = "crypto.invalid_configuration",
        httpStatusCode: int = 400,
    ) -> None:
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
        Exception.__init__(self, self.responseMessage)
