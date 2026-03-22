"""Tests for :class:`errors.UnauthorizedError`."""

from http import HTTPStatus

from errors import UnauthorizedError
from tests.core.errors.abstraction import IErrorsTests


class TestUnauthorizedError(IErrorsTests):
    def test_default_401(self):
        error = UnauthorizedError(
            responseMessage="Invalid token",
            responseKey="error_unauthorized",
        )
        assert error.httpStatusCode == HTTPStatus.UNAUTHORIZED
