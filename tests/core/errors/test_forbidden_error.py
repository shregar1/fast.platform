"""Tests for :class:`errors.ForbiddenError`."""
from tests.core.errors.abstraction import IErrorsTests


from http import HTTPStatus

from errors import ForbiddenError


class TestForbiddenError(IErrorsTests):
    def test_default_403(self):
        error = ForbiddenError(
            responseMessage="Denied",
            responseKey="error_forbidden",
        )
        assert error.httpStatusCode == HTTPStatus.FORBIDDEN
