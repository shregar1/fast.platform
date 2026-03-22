"""Tests for :class:`errors.NotFoundError`."""

from http import HTTPStatus

import pytest

from errors import NotFoundError
from tests.core.errors.abstraction import IErrorsTests


class TestNotFoundError(IErrorsTests):
    def test_creation(self):
        error = NotFoundError(
            responseMessage="User not found",
            responseKey="error_user_not_found",
            httpStatusCode=HTTPStatus.NOT_FOUND,
        )
        assert error.responseMessage == "User not found"
        assert error.responseKey == "error_user_not_found"
        assert error.httpStatusCode == HTTPStatus.NOT_FOUND

    def test_is_exception(self):
        error = NotFoundError(
            responseMessage="Test",
            responseKey="test",
            httpStatusCode=HTTPStatus.NOT_FOUND,
        )
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError(
                responseMessage="Resource not found",
                responseKey="error_resource_not_found",
                httpStatusCode=HTTPStatus.NOT_FOUND,
            )
        assert exc_info.value.responseMessage == "Resource not found"
