"""Tests for :class:`errors.UnsupportedLLMProviderError`."""

from http import HTTPStatus

from errors import UnsupportedLLMProviderError
from tests.core.errors.abstraction import IErrorsTests


class TestUnsupportedLLMProviderError(IErrorsTests):
    def test_provider_field(self) -> None:
        err = UnsupportedLLMProviderError("foo")
        assert err.provider == "foo"
        assert "foo" in err.responseMessage
        assert err.responseKey == "llm.unsupported_provider"
        assert err.httpStatusCode == HTTPStatus.BAD_REQUEST
