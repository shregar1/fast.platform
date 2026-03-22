"""Tests for :class:`errors.ConflictError`."""
from tests.core.errors.abstraction import IErrorsTests


from http import HTTPStatus

from errors import ConflictError


class TestConflictError(IErrorsTests):
    def test_default_409(self):
        error = ConflictError(
            responseMessage="Conflict",
            responseKey="error_conflict",
        )
        assert error.httpStatusCode == HTTPStatus.CONFLICT
