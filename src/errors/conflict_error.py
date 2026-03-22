"""Resource / state conflict (HTTP 409)."""

from .error import IError


class ConflictError(IError):
    """
    Exception for resource or state conflicts (409).

    Raised when the operation conflicts with the current state
    (e.g. duplicate resource, concurrent update, business rule).
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int = 409,
    ) -> None:
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
