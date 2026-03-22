"""Tests for :class:`errors.BadInputError`."""

from http import HTTPStatus

import pytest

from errors import BadInputError
from tests.core.errors.abstraction import IErrorsTests


class TestBadInputError(IErrorsTests):
    def test_creation(self):
        error = BadInputError(
            responseMessage="Invalid email format",
            responseKey="error_invalid_email",
            httpStatusCode=HTTPStatus.BAD_REQUEST,
        )
        assert error.responseMessage == "Invalid email format"
        assert error.responseKey == "error_invalid_email"
        assert error.httpStatusCode == HTTPStatus.BAD_REQUEST

    def test_is_exception(self):
        error = BadInputError(
            responseMessage="Test",
            responseKey="test",
            httpStatusCode=HTTPStatus.BAD_REQUEST,
        )
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        with pytest.raises(BadInputError) as exc_info:
            raise BadInputError(
                responseMessage="Test error",
                responseKey="error_test",
                httpStatusCode=HTTPStatus.BAD_REQUEST,
            )
        assert exc_info.value.responseMessage == "Test error"
