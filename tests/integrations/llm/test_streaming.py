"""Module test_streaming.py."""

from __future__ import annotations

"""Streaming iterators."""
import types
from typing import Any, AsyncIterator

import pytest

from fast_platform.integrations.llm.streaming import StreamChunk, iter_llm_stream, iter_openai_chat_stream
from tests.integrations.llm.abstraction import ILLMTests


async def _mock_openai_stream() -> AsyncIterator[Any]:
    """Execute _mock_openai_stream operation.

    Returns:
        The result of the operation.
    """
    ch = types.SimpleNamespace(
        choices=[
            types.SimpleNamespace(delta=types.SimpleNamespace(content="hello"), finish_reason=None)
        ]
    )
    yield ch
    u = types.SimpleNamespace(
        choices=[],
        usage=types.SimpleNamespace(prompt_tokens=1, completion_tokens=2, total_tokens=3),
    )
    yield u


class TestStreaming(ILLMTests):
    """Represents the TestStreaming class."""

    @pytest.mark.asyncio
    async def test_iter_openai_chat_stream(self) -> None:
        """Execute test_iter_openai_chat_stream operation.

        Returns:
            The result of the operation.
        """
        chunks: list[StreamChunk] = []
        async for c in iter_openai_chat_stream(_mock_openai_stream()):
            chunks.append(c)
        assert chunks[0].text == "hello"
        assert chunks[0].provider == "openai"
        assert chunks[1].usage is not None
        assert chunks[1].usage.total_tokens == 3

    @pytest.mark.asyncio
    async def test_iter_llm_stream_openai(self) -> None:
        """Execute test_iter_llm_stream_openai operation.

        Returns:
            The result of the operation.
        """
        n = 0
        async for _ in iter_llm_stream("openai", _mock_openai_stream()):
            n += 1
        assert n == 2
