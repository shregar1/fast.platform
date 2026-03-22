"""
Unified async iterators for OpenAI and Anthropic streaming chat/message APIs.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, AsyncIterator, Literal, Optional

from .token_usage import TokenUsage


@dataclass(slots=True)
class StreamChunk:
    """One piece of streamed text (and optional final usage on the last chunk)."""

    text: str
    provider: Literal["openai", "anthropic"]
    finish_reason: Optional[str] = None
    usage: Optional[TokenUsage] = None


async def iter_openai_chat_stream(stream: Any) -> AsyncIterator[StreamChunk]:
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
            yield StreamChunk(text=piece, provider="openai", finish_reason=fr)
        u = getattr(chunk, "usage", None)
        if u is not None:
            yield StreamChunk(
                text="",
                provider="openai",
                usage=TokenUsage.from_openai_completion(chunk, model=""),
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
    provider: Literal["openai", "anthropic"],
    stream: Any,
) -> AsyncIterator[StreamChunk]:
    """Dispatch to :func:`iter_openai_chat_stream` or :func:`iter_anthropic_message_stream`."""
    if provider == "openai":
        async for c in iter_openai_chat_stream(stream):
            yield c
    elif provider == "anthropic":
        async for c in iter_anthropic_message_stream(stream):
            yield c
    else:
        raise ValueError(f"unsupported provider: {provider!r}")
