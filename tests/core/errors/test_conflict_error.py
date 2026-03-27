"""Tests for :class:`errors.ConflictError`."""

from http import HTTPStatus

from fast_platform.core.errors import ConflictError
from tests.core.errors.abstraction import IErrorsTests


class TestConflictError(IErrorsTests):
    """Represents the TestConflictError class."""

    def test_default_409(self):
        """Execute test_default_409 operation.

        Returns:
            The result of the operation.
        """
        error = ConflictError(
            responseMessage="Conflict",
            responseKey="error_conflict",
        )
        assert error.httpStatusCode == HTTPStatus.CONFLICT
