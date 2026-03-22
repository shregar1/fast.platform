"""Tests for :class:`errors.LLMFeatureNotAvailableError`."""
from tests.core.errors.abstraction import IErrorsTests


from http import HTTPStatus

from errors import LLMFeatureNotAvailableError


class TestLLMFeatureNotAvailableError(IErrorsTests):
    def test_default_501(self) -> None:
        err = LLMFeatureNotAvailableError("not wired yet")
        assert err.responseMessage == "not wired yet"
        assert err.httpStatusCode == HTTPStatus.NOT_IMPLEMENTED
