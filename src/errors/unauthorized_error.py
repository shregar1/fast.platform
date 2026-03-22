"""Authentication failures (HTTP 401)."""

from .abstraction import IError


class UnauthorizedError(IError):
    """
    Exception for authentication failures (401).

    Raised when credentials are missing, invalid, or expired.
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int = 401,
    ) -> None:
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
