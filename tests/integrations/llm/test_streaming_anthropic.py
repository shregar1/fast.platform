from __future__ import annotations

"""Anthropic streaming iterator."""
import types

import pytest

from llm.streaming import iter_anthropic_message_stream
from tests.integrations.llm.abstraction import ILLMTests


class TestStreamingAnthropic(ILLMTests):
    @pytest.mark.asyncio
    async def test_iter_anthropic_message_stream(self) -> None:
        async def text_gen():
            yield "a"
            yield "b"

        class Stream:
            text_stream = text_gen()

            async def get_final_message(self):
                return types.SimpleNamespace(
                    usage=types.SimpleNamespace(input_tokens=2, output_tokens=3)
                )

        chunks = []
        async for c in iter_anthropic_message_stream(Stream()):
            chunks.append(c)
        assert chunks[0].text == "a"
        assert chunks[1].text == "b"
        assert chunks[-1].usage is not None
        assert chunks[-1].usage.total_tokens == 5
