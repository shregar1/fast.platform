"""
Unified async iterators for OpenAI and Anthropic streaming chat/message APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, AsyncIterator, Literal, Optional
import inspect

from errors.llm_feature_not_available_error import LLMFeatureNotAvailableError
from errors.unsupported_llm_provider_error import UnsupportedLLMProviderError

from .token_usage import TokenUsage


OpenAICompatibleStreamProvider = Literal["openai", "groq", "mistral"]


@dataclass(slots=True)
class StreamChunk:
    """One piece of streamed text (and optional final usage on the last chunk)."""

    text: str
    provider: Literal["openai", "anthropic", "groq", "mistral", "gemini"]
    finish_reason: Optional[str] = None
    usage: Optional[TokenUsage] = None


async def iter_openai_chat_stream(
    stream: Any,
    *,
    stream_provider: OpenAICompatibleStreamProvider = "openai",
) -> AsyncIterator[StreamChunk]:
    """
    Iterate an OpenAI ``AsyncStream`` from ``chat.completions.create(..., stream=True)``.

    Yields text deltas; if a chunk includes ``usage``, emits a :class:`StreamChunk`
    with ``usage`` set (often with empty ``text``).
    """
    async for chunk in stream:
        ch0 = chunk.choices[0] if chunk.choices else None
        delta = getattr(ch0, "delta", None) if ch0 else None
        piece = getattr(delta, "content", None) if delta else None
        if piece:
            fr = getattr(ch0, "finish_reason", None) if ch0 else None
            yield StreamChunk(text=piece, provider=stream_provider, finish_reason=fr)
        u = getattr(chunk, "usage", None)
        if u is not None:
            yield StreamChunk(
                text="",
                provider=stream_provider,
                usage=TokenUsage.from_openai_completion(
                    chunk,
                    model="",
                    provider=stream_provider,
                ),
            )


async def iter_anthropic_message_stream(stream: Any) -> AsyncIterator[StreamChunk]:
    """
    Iterate the ``text_stream`` of an Anthropic ``MessageStream`` (from ``messages.stream``).

    After text completes, calls ``get_final_message()`` when present and yields usage.
    """
    text_stream = getattr(stream, "text_stream", None)
    if text_stream is None:
        raise TypeError(
            "Anthropic stream must expose text_stream (e.g. async with client.messages.stream(...))"
        )
    async for piece in text_stream:
        if piece:
            yield StreamChunk(text=str(piece), provider="anthropic")
    gfm = getattr(stream, "get_final_message", None)
    if callable(gfm):
        msg = gfm()
        if inspect.isawaitable(msg):
            msg = await msg  # type: ignore[assignment]
        if msg is not None:
            u = TokenUsage.from_anthropic_message(msg, model="")
            yield StreamChunk(text="", provider="anthropic", usage=u)


async def iter_llm_stream(
    provider: Literal["openai", "anthropic", "groq", "mistral", "gemini"],
    stream: Any,
) -> AsyncIterator[StreamChunk]:
    """Dispatch to OpenAI-compatible, Anthropic, or (future) Gemini stream helpers."""
    if provider in ("openai", "groq", "mistral"):
        async for c in iter_openai_chat_stream(stream, stream_provider=provider):
            yield c
    elif provider == "anthropic":
        async for c in iter_anthropic_message_stream(stream):
            yield c
    elif provider == "gemini":
        raise LLMFeatureNotAvailableError(
            "Gemini streaming is not wired here yet; use the google-generativeai "
            "async stream API directly.",
            responseKey="llm.gemini_streaming_not_wired",
        )
    else:
        raise UnsupportedLLMProviderError(provider)
