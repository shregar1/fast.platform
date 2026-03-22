"""
Unexpected failures (:class:`UnexpectedResponseError`).
"""

from .error import IError


class UnexpectedResponseError(IError):
    """
    Exception for unexpected conditions (5xx, 502, etc.).

    Attributes:
        responseMessage: Human-readable description.
        responseKey: Machine-readable key (e.g. for i18n).
        httpStatusCode: HTTP status to return.
    """

    def __init__(
        self,
        responseMessage: str,
        responseKey: str,
        httpStatusCode: int,
    ) -> None:
        super().__init__()
        self.responseMessage = responseMessage
        self.responseKey = responseKey
        self.httpStatusCode = httpStatusCode
