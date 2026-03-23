"""
Bad input / validation errors (:class:`BadInputError`).
"""

from .abstraction import IError


class BadInputError(IError):
    """
    Exception for invalid input (typically HTTP 400).

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
