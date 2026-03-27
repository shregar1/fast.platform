"""Tests for :class:`errors.ServiceUnavailableError`."""

from http import HTTPStatus

from fast_platform.core.errors import ServiceUnavailableError
from tests.core.errors.abstraction import IErrorsTests


class TestServiceUnavailableError(IErrorsTests):
    """Represents the TestServiceUnavailableError class."""

    def test_default_503(self):
        """Execute test_default_503 operation.

        Returns:
            The result of the operation.
        """
        error = ServiceUnavailableError(
            responseMessage="Down",
            responseKey="error_unavailable",
        )
        assert error.httpStatusCode == HTTPStatus.SERVICE_UNAVAILABLE
