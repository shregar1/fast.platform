"""Temporary dependency / service unavailability (HTTP 503)."""

from .error import IError


class ServiceUnavailableError(IError):
    """
    Exception for temporary unavailability (503).

    Raised when a required service or dependency is temporarily unavailable.
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int = 503,
    ) -> None:
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
