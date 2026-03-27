"""Tests for :class:`errors.UnexpectedResponseError`."""

from http import HTTPStatus

import pytest

from fast_platform.core.errors import UnexpectedResponseError
from tests.core.errors.abstraction import IErrorsTests


class TestUnexpectedResponseError(IErrorsTests):
    """Represents the TestUnexpectedResponseError class."""

    def test_creation(self):
        """Execute test_creation operation.

        Returns:
            The result of the operation.
        """
        error = UnexpectedResponseError(
            responseMessage="Unexpected error occurred",
            responseKey="error_unexpected",
            httpStatusCode=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        assert error.responseMessage == "Unexpected error occurred"
        assert error.responseKey == "error_unexpected"
        assert error.httpStatusCode == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_is_exception(self):
        """Execute test_is_exception operation.

        Returns:
            The result of the operation.
        """
        error = UnexpectedResponseError(
            responseMessage="Test",
            responseKey="test",
            httpStatusCode=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        """Execute test_can_be_raised operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(UnexpectedResponseError) as exc_info:
            raise UnexpectedResponseError(
                responseMessage="Service unavailable",
                responseKey="error_service",
                httpStatusCode=HTTPStatus.SERVICE_UNAVAILABLE,
            )
        assert exc_info.value.responseMessage == "Service unavailable"

    def test_different_status_codes(self):
        """Execute test_different_status_codes operation.

        Returns:
            The result of the operation.
        """
        error = UnexpectedResponseError(
            responseMessage="Bad gateway",
            responseKey="error_gateway",
            httpStatusCode=HTTPStatus.BAD_GATEWAY,
        )
        assert error.httpStatusCode == HTTPStatus.BAD_GATEWAY
