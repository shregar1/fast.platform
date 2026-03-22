"""Tests for :class:`errors.UnexpectedResponseError`."""

from http import HTTPStatus

import pytest

from errors import UnexpectedResponseError
from tests.core.errors.abstraction import IErrorsTests


class TestUnexpectedResponseError(IErrorsTests):
    def test_creation(self):
        error = UnexpectedResponseError(
            responseMessage="Unexpected error occurred",
            responseKey="error_unexpected",
            httpStatusCode=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        assert error.responseMessage == "Unexpected error occurred"
        assert error.responseKey == "error_unexpected"
        assert error.httpStatusCode == HTTPStatus.INTERNAL_SERVER_ERROR

    def test_is_exception(self):
        error = UnexpectedResponseError(
            responseMessage="Test",
            responseKey="test",
            httpStatusCode=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        with pytest.raises(UnexpectedResponseError) as exc_info:
            raise UnexpectedResponseError(
                responseMessage="Service unavailable",
                responseKey="error_service",
                httpStatusCode=HTTPStatus.SERVICE_UNAVAILABLE,
            )
        assert exc_info.value.responseMessage == "Service unavailable"

    def test_different_status_codes(self):
        error = UnexpectedResponseError(
            responseMessage="Bad gateway",
            responseKey="error_gateway",
            httpStatusCode=HTTPStatus.BAD_GATEWAY,
        )
        assert error.httpStatusCode == HTTPStatus.BAD_GATEWAY
