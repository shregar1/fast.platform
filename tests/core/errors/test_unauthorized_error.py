"""Tests for :class:`errors.UnauthorizedError`."""

from http import HTTPStatus

from core.errors import UnauthorizedError
from tests.core.errors.abstraction import IErrorsTests


class TestUnauthorizedError(IErrorsTests):
    """Represents the TestUnauthorizedError class."""

    def test_default_401(self):
        """Execute test_default_401 operation.

        Returns:
            The result of the operation.
        """
        error = UnauthorizedError(
            responseMessage="Invalid token",
            responseKey="error_unauthorized",
        )
        assert error.httpStatusCode == HTTPStatus.UNAUTHORIZED
