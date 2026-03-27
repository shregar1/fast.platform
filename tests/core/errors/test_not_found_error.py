"""Tests for :class:`errors.NotFoundError`."""

from http import HTTPStatus

import pytest

from core.errors import NotFoundError
from tests.core.errors.abstraction import IErrorsTests


class TestNotFoundError(IErrorsTests):
    """Represents the TestNotFoundError class."""

    def test_creation(self):
        """Execute test_creation operation.

        Returns:
            The result of the operation.
        """
        error = NotFoundError(
            responseMessage="User not found",
            responseKey="error_user_not_found",
            httpStatusCode=HTTPStatus.NOT_FOUND,
        )
        assert error.responseMessage == "User not found"
        assert error.responseKey == "error_user_not_found"
        assert error.httpStatusCode == HTTPStatus.NOT_FOUND

    def test_is_exception(self):
        """Execute test_is_exception operation.

        Returns:
            The result of the operation.
        """
        error = NotFoundError(
            responseMessage="Test",
            responseKey="test",
            httpStatusCode=HTTPStatus.NOT_FOUND,
        )
        assert isinstance(error, BaseException)

    def test_can_be_raised(self):
        """Execute test_can_be_raised operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError(
                responseMessage="Resource not found",
                responseKey="error_resource_not_found",
                httpStatusCode=HTTPStatus.NOT_FOUND,
            )
        assert exc_info.value.responseMessage == "Resource not found"
