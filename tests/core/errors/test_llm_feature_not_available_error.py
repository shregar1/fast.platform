"""Tests for :class:`errors.LLMFeatureNotAvailableError`."""

from http import HTTPStatus

from fast_platform.core.errors import LLMFeatureNotAvailableError
from tests.core.errors.abstraction import IErrorsTests


class TestLLMFeatureNotAvailableError(IErrorsTests):
    """Represents the TestLLMFeatureNotAvailableError class."""

    def test_default_501(self) -> None:
        """Execute test_default_501 operation.

        Returns:
            The result of the operation.
        """
        err = LLMFeatureNotAvailableError("not wired yet")
        assert err.responseMessage == "not wired yet"
        assert err.httpStatusCode == HTTPStatus.NOT_IMPLEMENTED
