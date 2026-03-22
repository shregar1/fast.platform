"""Tests for :class:`errors.TokenBudgetExceeded`."""
from tests.core.errors.abstraction import IErrorsTests


from http import HTTPStatus

from errors import TokenBudgetExceeded


class TestTokenBudgetExceeded(IErrorsTests):
    def test_limits_and_429(self) -> None:
        err = TokenBudgetExceeded(10, 20)
        assert err.limit == 10
        assert err.cumulative == 20
        assert err.responseKey == "llm.token_budget_exceeded"
        assert err.httpStatusCode == HTTPStatus.TOO_MANY_REQUESTS
