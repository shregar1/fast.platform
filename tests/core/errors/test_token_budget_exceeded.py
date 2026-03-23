"""Tests for :class:`errors.TokenBudgetExceeded`."""

from http import HTTPStatus

from core.errors import TokenBudgetExceeded
from tests.core.errors.abstraction import IErrorsTests


class TestTokenBudgetExceeded(IErrorsTests):
    def test_limits_and_429(self) -> None:
        err = TokenBudgetExceeded(10, 20)
        assert err.limit == 10
        assert err.cumulative == 20
        assert err.responseKey == "llm.token_budget_exceeded"
        assert err.httpStatusCode == HTTPStatus.TOO_MANY_REQUESTS
