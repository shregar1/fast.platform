"""Token usage metrics for LLM completions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Union

TokenUsageCallback = Callable[["TokenUsage"], Union[None, Any]]


@dataclass(slots=True)
class TokenUsage:
    """Normalized usage for metrics / logging."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str = ""
    provider: str = ""

    @classmethod
    def from_openai_completion(
        cls,
        resp: Any,
        *,
        model: str = "",
        provider: str = "openai",
    ) -> "TokenUsage":
        """Execute from_openai_completion operation.

        Args:
            resp: The resp parameter.
            model: The model parameter.
            provider: The provider parameter.

        Returns:
            The result of the operation.
        """
        u = getattr(resp, "usage", None)
        if u is None:
            return cls(0, 0, 0, model=model, provider=provider)
        pt = int(getattr(u, "prompt_tokens", 0) or 0)
        ct = int(getattr(u, "completion_tokens", 0) or 0)
        tt = int(getattr(u, "total_tokens", 0) or (pt + ct))
        return cls(pt, ct, tt, model=model, provider=provider)

    @classmethod
    def from_anthropic_message(cls, resp: Any, *, model: str = "") -> "TokenUsage":
        """Execute from_anthropic_message operation.

        Args:
            resp: The resp parameter.
            model: The model parameter.

        Returns:
            The result of the operation.
        """
        u = getattr(resp, "usage", None)
        if u is None:
            return cls(0, 0, 0, model=model, provider="anthropic")
        it = int(getattr(u, "input_tokens", 0) or 0)
        ot = int(getattr(u, "output_tokens", 0) or 0)
        return cls(it, ot, it + ot, model=model, provider="anthropic")

    @classmethod
    def from_gemini_response(cls, resp: Any, *, model: str = "") -> "TokenUsage":
        """Execute from_gemini_response operation.

        Args:
            resp: The resp parameter.
            model: The model parameter.

        Returns:
            The result of the operation.
        """
        u = getattr(resp, "usage_metadata", None)
        if u is None:
            return cls(0, 0, 0, model=model, provider="gemini")
        pt = int(getattr(u, "prompt_token_count", 0) or 0)
        ct = int(getattr(u, "candidates_token_count", 0) or 0)
        tt = int(getattr(u, "total_token_count", 0) or (pt + ct))
        return cls(pt, ct, tt, model=model, provider="gemini")
