"""Tests for :class:`errors.ServiceUnavailableError`."""
from tests.core.errors.abstraction import IErrorsTests


from http import HTTPStatus

from errors import ServiceUnavailableError


class TestServiceUnavailableError(IErrorsTests):
    def test_default_503(self):
        error = ServiceUnavailableError(
            responseMessage="Down",
            responseKey="error_unavailable",
        )
        assert error.httpStatusCode == HTTPStatus.SERVICE_UNAVAILABLE
