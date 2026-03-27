"""Tests for :class:`errors.CryptoConfigurationError`."""

from http import HTTPStatus

from fast_platform.core.errors import CryptoConfigurationError
from tests.core.errors.abstraction import IErrorsTests


class TestCryptoConfigurationError(IErrorsTests):
    """Represents the TestCryptoConfigurationError class."""

    def test_creation(self) -> None:
        """Execute test_creation operation.

        Returns:
            The result of the operation.
        """
        err = CryptoConfigurationError("bad", responseKey="crypto.test")
        assert err.responseMessage == "bad"
        assert err.responseKey == "crypto.test"
        assert err.httpStatusCode == HTTPStatus.BAD_REQUEST
