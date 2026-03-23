"""Tests for :class:`errors.RateLimitError`."""

from http import HTTPStatus

from core.errors import RateLimitError
from tests.core.errors.abstraction import IErrorsTests


class TestRateLimitError(IErrorsTests):
    def test_default_429(self):
        error = RateLimitError(
            responseMessage="Too many",
            responseKey="error_rate_limit",
        )
        assert error.httpStatusCode == HTTPStatus.TOO_MANY_REQUESTS
