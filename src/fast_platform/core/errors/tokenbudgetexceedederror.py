"""Hard token budget exceeded for LLM streams (HTTP 429)."""

from __future__ import annotations

from .abstraction import IError


class TokenBudgetExceeded(IError):
    """Raised when cumulative token usage exceeds a configured limit."""

    def __init__(self, limit: int, cumulative: int, message: str = "") -> None:
        """Execute __init__ operation.

        Args:
            limit: The limit parameter.
            cumulative: The cumulative parameter.
            message: The message parameter.
        """
        self.limit = limit
        self.cumulative = cumulative
        m = message or f"token budget exceeded: cumulative={cumulative} > limit={limit}"
        super().__init__()
        self.responseMessage = m
        self.responseKey = "llm.token_budget_exceeded"
        self.httpStatusCode = 429
        Exception.__init__(self, m)
