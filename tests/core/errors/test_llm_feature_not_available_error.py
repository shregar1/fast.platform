"""Tests for :class:`errors.LLMFeatureNotAvailableError`."""

from http import HTTPStatus

from core.errors import LLMFeatureNotAvailableError
from tests.core.errors.abstraction import IErrorsTests


class TestLLMFeatureNotAvailableError(IErrorsTests):
    def test_default_501(self) -> None:
        err = LLMFeatureNotAvailableError("not wired yet")
        assert err.responseMessage == "not wired yet"
        assert err.httpStatusCode == HTTPStatus.NOT_IMPLEMENTED
