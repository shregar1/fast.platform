"""
LLM provider implementations (OpenAI, Anthropic, Ollama) and factory.

These live in ``fast_llm`` so the package stays usable without a separate ``from fast_platform.services`` tree.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, Protocol, runtime_checkable

from from fast_platform import LLMConfiguration


@runtime_checkable
class ILLMService(Protocol):
    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        """Run a single user-message completion and return assistant text."""


class OpenAILLMService:
    """Thin async wrapper around the OpenAI chat completions API."""

    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("openai package required: pip install fast_llm[openai]") from e
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content or ""


class AnthropicLLMService:
    """Thin async wrapper around Anthropic Messages API."""

    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        try:
            from anthropic import AsyncAnthropic
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("anthropic package required: pip install fast_llm[anthropic]") from e
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


class OllamaLLMService:
    """Call a local Ollama server over HTTP (``/api/chat``)."""

    def __init__(self, base_url: str, model: str) -> None:
        try:
            import httpx
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("httpx required: pip install fast_llm[ollama]") from e
        self._httpx = httpx
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        async with self._httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "options": {"num_predict": max_tokens},
                },
            )
            r.raise_for_status()
            data = r.json()
            msg = data.get("message") or {}
            return str(msg.get("content") or "")


def build_llm_service(
    provider: Literal["openai", "anthropic", "ollama"] = "openai",
) -> Optional[ILLMService]:
    """Build a provider from :class:`LLMConfiguration` (``config/llm/config.json``)."""
    cfg = LLMConfiguration().get_config()
    if provider == "openai":
        o = cfg.openai
        if getattr(o, "enabled", False) and o.api_key and o.model:
            return OpenAILLMService(o.api_key, o.base_url, o.model)
    if provider == "anthropic":
        a = cfg.anthropic
        if getattr(a, "enabled", False) and a.api_key and a.model:
            return AnthropicLLMService(a.api_key, a.base_url, a.model)
    if provider == "ollama":
        ol = cfg.ollama
        if getattr(ol, "enabled", False) and ol.base_url and ol.model:
            return OllamaLLMService(ol.base_url, ol.model)
    return None
