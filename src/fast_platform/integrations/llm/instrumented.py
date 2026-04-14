"""OpenAI / Anthropic LLM services with optional per-completion token usage callbacks."""

from __future__ import annotations

from .constants import OPENAI_PROVIDER
import inspect
from typing import Any, Optional

from .constants import GROQ_DEFAULT_BASE_URL, MISTRAL_DEFAULT_BASE_URL
from .providers import AnthropicLLMService, GeminiLLMService, OpenAILLMService
from .token_usage import TokenUsage, TokenUsageCallback


async def _maybe_await(coro_or_none: Any) -> None:
    """Execute _maybe_await operation.

    Args:
        coro_or_none: The coro_or_none parameter.

    Returns:
        The result of the operation.
    """
    if coro_or_none is None:
        return
    if inspect.isawaitable(coro_or_none):
        await coro_or_none


class InstrumentedOpenAILLMService(OpenAILLMService):
    """Like :class:`OpenAILLMService` but invokes ``on_token_usage`` after each completion."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str],
        model: str,
        *,
        on_token_usage: Optional[TokenUsageCallback] = None,
        usage_provider: str = OPENAI_PROVIDER,
    ) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            base_url: The base_url parameter.
            model: The model parameter.
            on_token_usage: The on_token_usage parameter.
            usage_provider: The usage_provider parameter.
        """
        super().__init__(api_key, base_url, model)
        self._on_token_usage = on_token_usage
        self._usage_provider = usage_provider

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        """Execute generate operation.

        Args:
            prompt: The prompt parameter.
            max_tokens: The max_tokens parameter.

        Returns:
            The result of the operation.
        """
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        text = resp.choices[0].message.content or ""
        if self._on_token_usage:
            u = TokenUsage.from_openai_completion(
                resp,
                model=self._model,
                provider=self._usage_provider,
            )
            await _maybe_await(self._on_token_usage(u))
        return text


class InstrumentedGroqLLMService(InstrumentedOpenAILLMService):
    """Instrumented Groq (OpenAI-compatible) completions."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str],
        model: str,
        *,
        on_token_usage: Optional[TokenUsageCallback] = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            base_url: The base_url parameter.
            model: The model parameter.
            on_token_usage: The on_token_usage parameter.
        """
        super().__init__(
            api_key,
            base_url or GROQ_DEFAULT_BASE_URL,
            model,
            on_token_usage=on_token_usage,
            usage_provider="groq",
        )


class InstrumentedMistralLLMService(InstrumentedOpenAILLMService):
    """Instrumented Mistral (OpenAI-compatible) completions."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str],
        model: str,
        *,
        on_token_usage: Optional[TokenUsageCallback] = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            base_url: The base_url parameter.
            model: The model parameter.
            on_token_usage: The on_token_usage parameter.
        """
        super().__init__(
            api_key,
            base_url or MISTRAL_DEFAULT_BASE_URL,
            model,
            on_token_usage=on_token_usage,
            usage_provider="mistral",
        )


class InstrumentedGeminiLLMService(GeminiLLMService):
    """Like :class:`GeminiLLMService` but invokes ``on_token_usage`` after each completion."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: Optional[str] = None,
        *,
        on_token_usage: Optional[TokenUsageCallback] = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            model: The model parameter.
            base_url: The base_url parameter.
            on_token_usage: The on_token_usage parameter.
        """
        super().__init__(api_key, model, base_url)
        self._on_token_usage = on_token_usage

    async def generate(self, prompt: str, *, max_tokens: int = 256) -> str:
        """Execute generate operation.

        Args:
            prompt: The prompt parameter.
            max_tokens: The max_tokens parameter.

        Returns:
            The result of the operation.
        """
        resp = await self._generate_response(prompt, max_tokens=max_tokens)
        text = self._extract_text(resp)
        if self._on_token_usage:
            u = TokenUsage.from_gemini_response(resp, model=self._model_name)
            await _maybe_await(self._on_token_usage(u))
        return text


class InstrumentedAnthropicLLMService(AnthropicLLMService):
    """Like :class:`AnthropicLLMService` but invokes ``on_token_usage`` after each completion."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str],
        model: str,
        *,
        on_token_usage: Optional[TokenUsageCallback] = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            base_url: The base_url parameter.
            model: The model parameter.
            on_token_usage: The on_token_usage parameter.
        """
        super().__init__(api_key, base_url, model)
        self._on_token_usage = on_token_usage

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
        text = "".join(text_parts)
        if self._on_token_usage:
            u = TokenUsage.from_anthropic_message(resp, model=self._model)
            await _maybe_await(self._on_token_usage(u))
        return text
