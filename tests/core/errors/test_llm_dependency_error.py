"""Tests for :class:`errors.LLMDependencyError`."""

from http import HTTPStatus

from fast_platform.core.errors import LLMDependencyError
from tests.core.errors.abstraction import IErrorsTests


class TestLLMDependencyError(IErrorsTests):
    """Represents the TestLLMDependencyError class."""

    def test_message_and_keys(self) -> None:
        """Execute test_message_and_keys operation.

        Returns:
            The result of the operation.
        """
        err = LLMDependencyError(provider="openai", pip_extra="fast_llm[openai]")
        assert "openai" in err.responseMessage
        assert "fast_llm[openai]" in err.responseMessage
        assert err.responseKey == "llm.missing_dependency"
        assert err.httpStatusCode == HTTPStatus.SERVICE_UNAVAILABLE
        assert "pip install" in str(err)
