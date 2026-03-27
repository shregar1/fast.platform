"""Tests for :class:`errors.UnsupportedLLMProviderError`."""

from http import HTTPStatus

from fast_platform.core.errors import UnsupportedLLMProviderError
from tests.core.errors.abstraction import IErrorsTests


class TestUnsupportedLLMProviderError(IErrorsTests):
    """Represents the TestUnsupportedLLMProviderError class."""

    def test_provider_field(self) -> None:
        """Execute test_provider_field operation.

        Returns:
            The result of the operation.
        """
        err = UnsupportedLLMProviderError("foo")
        assert err.provider == "foo"
        assert "foo" in err.responseMessage
        assert err.responseKey == "llm.unsupported_provider"
        assert err.httpStatusCode == HTTPStatus.BAD_REQUEST
