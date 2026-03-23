"""Anthropic Messages API."""

from __future__ import annotations

from typing import Any, Optional

from core.errors.llm_dependency_error import LLMDependencyError


class AnthropicLLMService:
    """Thin async wrapper around Anthropic Messages API."""

    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        try:
            from anthropic import AsyncAnthropic
        except ImportError as e:  # pragma: no cover
            raise LLMDependencyError(
                provider="anthropic",
                pip_extra="fast_llm[anthropic]",
                cause=e,
            ) from e
        kwargs: dict[str, Any] = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = AsyncAnthropic(**kwargs)
        self._model = model

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        resp = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = resp.content or []
        text_parts: list[str] = []
        for p in parts:
            if getattr(p, "type", None) == "text":
                text_parts.append(getattr(p, "text", ""))
        return "".join(text_parts)


__all__ = ["AnthropicLLMService"]
