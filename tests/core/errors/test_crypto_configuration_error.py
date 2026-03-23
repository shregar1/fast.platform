"""Tests for :class:`errors.CryptoConfigurationError`."""

from http import HTTPStatus

from core.errors import CryptoConfigurationError
from tests.core.errors.abstraction import IErrorsTests


class TestCryptoConfigurationError(IErrorsTests):
    def test_creation(self) -> None:
        err = CryptoConfigurationError("bad", responseKey="crypto.test")
        assert err.responseMessage == "bad"
        assert err.responseKey == "crypto.test"
        assert err.httpStatusCode == HTTPStatus.BAD_REQUEST
