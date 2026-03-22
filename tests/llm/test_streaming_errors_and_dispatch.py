"""Streaming edge cases: TypeError, ValueError, async get_final_message."""

from __future__ import annotations

import types
from typing import Any, cast

import pytest

from llm.streaming import iter_anthropic_message_stream, iter_llm_stream


@pytest.mark.asyncio
async def test_anthropic_stream_missing_text_stream() -> None:
    class Bad:
        pass

    with pytest.raises(TypeError, match="text_stream"):
        async for _ in iter_anthropic_message_stream(Bad()):
            pass


@pytest.mark.asyncio
async def test_iter_llm_stream_bad_provider() -> None:
    async def empty():
        if False:
            yield None

    with pytest.raises(ValueError, match="unsupported"):
        async for _ in iter_llm_stream(cast(Any, "gemini"), empty()):
            pass


@pytest.mark.asyncio
async def test_anthropic_get_final_message_awaitable() -> None:
    async def text_gen():
        yield "z"

    class Stream:
        text_stream = text_gen()

        async def get_final_message(self):
            return types.SimpleNamespace(
                usage=types.SimpleNamespace(input_tokens=1, output_tokens=1)
            )

    chunks = []
    async for c in iter_anthropic_message_stream(Stream()):
        chunks.append(c)
    assert chunks[-1].usage is not None


@pytest.mark.asyncio
async def test_anthropic_no_get_final_message() -> None:
    async def text_gen():
        yield "a"

    class Stream:
        text_stream = text_gen()

    chunks = []
    async for c in iter_anthropic_message_stream(Stream()):
        chunks.append(c)
    assert len(chunks) == 1
    assert chunks[0].usage is None
