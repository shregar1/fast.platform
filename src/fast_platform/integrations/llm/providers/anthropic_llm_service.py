"""Anthropic Messages API."""

from __future__ import annotations

from typing import Any, Optional

from core.errors.llm_dependency_error import LLMDependencyError


class AnthropicLLMService:
    """Thin async wrapper around Anthropic Messages API."""

    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            base_url: The base_url parameter.
            model: The model parameter.
        """
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
        """Execute generate operation.

        Args:
            prompt: The prompt parameter.
            max_tokens: The max_tokens parameter.

        Returns:
            The result of the operation.
        """
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
