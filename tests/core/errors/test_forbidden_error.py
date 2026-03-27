"""Tests for :class:`errors.ForbiddenError`."""

from http import HTTPStatus

from core.errors import ForbiddenError
from tests.core.errors.abstraction import IErrorsTests


class TestForbiddenError(IErrorsTests):
    """Represents the TestForbiddenError class."""

    def test_default_403(self):
        """Execute test_default_403 operation.

        Returns:
            The result of the operation.
        """
        error = ForbiddenError(
            responseMessage="Denied",
            responseKey="error_forbidden",
        )
        assert error.httpStatusCode == HTTPStatus.FORBIDDEN
