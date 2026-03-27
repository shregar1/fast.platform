"""Rate limit exceeded (HTTP 429)."""

from .abstraction import IError


class RateLimitError(IError):
    """Exception for rate limit exceeded (429).

    Raised when the client has made too many requests in a given window.
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int = 429,
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
