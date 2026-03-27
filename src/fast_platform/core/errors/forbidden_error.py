"""Authenticated but not allowed (HTTP 403)."""

from .abstraction import IError


class ForbiddenError(IError):
    """Exception for forbidden access (403).

    Raised when the user is authenticated but not authorized to
    perform the action.
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int = 403,
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
