"""Tests for :class:`errors.LLMDependencyError`."""

from http import HTTPStatus

from errors import LLMDependencyError
from tests.core.errors.abstraction import IErrorsTests


class TestLLMDependencyError(IErrorsTests):
    def test_message_and_keys(self) -> None:
        err = LLMDependencyError(provider="openai", pip_extra="fast_llm[openai]")
        assert "openai" in err.responseMessage
        assert "fast_llm[openai]" in err.responseMessage
        assert err.responseKey == "llm.missing_dependency"
        assert err.httpStatusCode == HTTPStatus.SERVICE_UNAVAILABLE
        assert "pip install" in str(err)
