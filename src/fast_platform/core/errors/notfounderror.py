"""Resource not found errors (:class:`NotFoundError`)."""

from .abstraction import IError


class NotFoundError(IError):
    """Exception when a resource does not exist (typically HTTP 404).

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
