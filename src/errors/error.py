"""
Base application error (:class:`IError`).

Extracted from ``fast_mvc_main/abstractions/error.py``.
"""

from loguru import Logger, logger


class IError(Exception):
    """
    Base exception class for all application-specific errors.

    Provides request context tracking and structured logging. Subclasses
    typically add ``responseMessage``, ``responseKey``, and ``httpStatusCode``.
    """

    def __init__(
        self,
        urn: str | None = None,
        user_urn: str | None = None,
        api_name: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self._urn = urn
        self._user_urn = user_urn
        self._api_name = api_name
        self._user_id = user_id
        self._logger = logger.bind(
            urn=self._urn,
            user_urn=self._user_urn,
            api_name=self._api_name,
            user_id=self._user_id,
        )

    @property
    def urn(self) -> str | None:
        return self._urn

    @urn.setter
    def urn(self, value: str | None) -> None:
        self._urn = value

    @property
    def user_urn(self) -> str | None:
        return self._user_urn

    @user_urn.setter
    def user_urn(self, value: str | None) -> None:
        self._user_urn = value

    @property
    def api_name(self) -> str | None:
        return self._api_name

    @api_name.setter
    def api_name(self, value: str | None) -> None:
        self._api_name = value

    @property
    def user_id(self) -> str | None:
        return self._user_id

    @user_id.setter
    def user_id(self, value: str | None) -> None:
        self._user_id = value

    @property
    def logger(self) -> Logger:
        return self._logger

    @logger.setter
    def logger(self, value: Logger) -> None:
        self._logger = value
