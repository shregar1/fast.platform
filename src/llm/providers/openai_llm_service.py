"""OpenAI chat completions API."""

from __future__ import annotations

from typing import Optional

from errors.llm_dependency_error import LLMDependencyError


class OpenAILLMService:
    """Thin async wrapper around the OpenAI chat completions API."""

    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as e:  # pragma: no cover
            raise LLMDependencyError(
                provider="openai",
                pip_extra="fast_llm[openai]",
                cause=e,
            ) from e
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""


__all__ = ["OpenAILLMService"]
