"""
Per-request token budget guards for streaming and non-streaming usage.

Use with :class:`~fast_llm.token_usage.TokenUsage` and :class:`~fast_llm.streaming.StreamChunk`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator

from errors.token_budget_exceeded_error import TokenBudgetExceeded

if TYPE_CHECKING:
    from .streaming import StreamChunk
    from .token_usage import TokenUsage


def check_usage_against_budget(usage: TokenUsage, max_total_tokens: int) -> None:
    """Raise :class:`TokenBudgetExceeded` if ``usage.total_tokens`` exceeds ``max_total_tokens``."""
    if usage.total_tokens > max_total_tokens:
        raise TokenBudgetExceeded(max_total_tokens, usage.total_tokens)


def estimate_tokens_from_text(text: str, *, chars_per_token: float = 4.0) -> int:
    """Rough token estimate for streaming deltas when usage is not yet available."""
    if not text:
        return 0
    return max(1, int(len(text) / chars_per_token))


async def iter_llm_stream_with_budget(
    stream: AsyncIterator[StreamChunk],
    *,
    max_total_tokens: int,
    estimate_text_until_usage: bool = True,
    chars_per_token: float = 4.0,
) -> AsyncIterator[StreamChunk]:
    """
    Wrap a unified LLM stream and enforce a **hard** cumulative cap.

    * When a chunk includes :attr:`StreamChunk.usage`, ``cumulative`` is set to
      :attr:`~fast_llm.token_usage.TokenUsage.total_tokens` (authoritative).
    * Until then, if ``estimate_text_until_usage`` is true, each text delta adds
      :func:`estimate_tokens_from_text` to a running estimate so the stream can stop early.

    Raises :class:`TokenBudgetExceeded` when the limit is exceeded.
    """
    cumulative = 0
    async for chunk in stream:
        if chunk.usage is not None:
            cumulative = chunk.usage.total_tokens
        elif estimate_text_until_usage and chunk.text:
            cumulative += estimate_tokens_from_text(chunk.text, chars_per_token=chars_per_token)
        if cumulative > max_total_tokens:
            raise TokenBudgetExceeded(max_total_tokens, cumulative)
        yield chunk
