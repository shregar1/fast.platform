"""Tests for errors."""

from http import HTTPStatus

import pytest

from errors import (
    BadInputError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnauthorizedError,
    UnexpectedResponseError,
)


class TestBadInputError:
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


class TestNotFoundError:
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


class TestUnexpectedResponseError:
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


class TestUnauthorizedError:
    def test_default_401(self):
        error = UnauthorizedError(
            responseMessage="Invalid token",
            responseKey="error_unauthorized",
        )
        assert error.httpStatusCode == HTTPStatus.UNAUTHORIZED


class TestForbiddenError:
    def test_default_403(self):
        error = ForbiddenError(
            responseMessage="Denied",
            responseKey="error_forbidden",
        )
        assert error.httpStatusCode == HTTPStatus.FORBIDDEN


class TestConflictError:
    def test_default_409(self):
        error = ConflictError(
            responseMessage="Conflict",
            responseKey="error_conflict",
        )
        assert error.httpStatusCode == HTTPStatus.CONFLICT


class TestRateLimitError:
    def test_default_429(self):
        error = RateLimitError(
            responseMessage="Too many",
            responseKey="error_rate_limit",
        )
        assert error.httpStatusCode == HTTPStatus.TOO_MANY_REQUESTS


class TestServiceUnavailableError:
    def test_default_503(self):
        error = ServiceUnavailableError(
            responseMessage="Down",
            responseKey="error_unavailable",
        )
        assert error.httpStatusCode == HTTPStatus.SERVICE_UNAVAILABLE
