"""Tests for :class:`errors.ConflictError`."""

from http import HTTPStatus

from core.errors import ConflictError
from tests.core.errors.abstraction import IErrorsTests


class TestConflictError(IErrorsTests):
    def test_default_409(self):
        error = ConflictError(
            responseMessage="Conflict",
            responseKey="error_conflict",
        )
        assert error.httpStatusCode == HTTPStatus.CONFLICT
