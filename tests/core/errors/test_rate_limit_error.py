"""Tests for :class:`errors.RateLimitError`."""

from http import HTTPStatus

from fast_platform.core.errors import RateLimitError
from tests.core.errors.abstraction import IErrorsTests


class TestRateLimitError(IErrorsTests):
    """Represents the TestRateLimitError class."""

    def test_default_429(self):
        """Execute test_default_429 operation.

        Returns:
            The result of the operation.
        """
        error = RateLimitError(
            responseMessage="Too many",
            responseKey="error_rate_limit",
        )
        assert error.httpStatusCode == HTTPStatus.TOO_MANY_REQUESTS
