"""Tests for :class:`errors.CryptoConfigurationError`."""
from tests.core.errors.abstraction import IErrorsTests


from http import HTTPStatus

from errors import CryptoConfigurationError


class TestCryptoConfigurationError(IErrorsTests):
    def test_creation(self) -> None:
        err = CryptoConfigurationError("bad", responseKey="crypto.test")
        assert err.responseMessage == "bad"
        assert err.responseKey == "crypto.test"
        assert err.httpStatusCode == HTTPStatus.BAD_REQUEST
