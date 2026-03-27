"""Module test_streaming_anthropic.py."""

from __future__ import annotations

"""Anthropic streaming iterator."""
import types

import pytest

from integrations.llm.streaming import iter_anthropic_message_stream
from tests.integrations.llm.abstraction import ILLMTests


class TestStreamingAnthropic(ILLMTests):
    """Represents the TestStreamingAnthropic class."""

    @pytest.mark.asyncio
    async def test_iter_anthropic_message_stream(self) -> None:
        """Execute test_iter_anthropic_message_stream operation.

        Returns:
            The result of the operation.
        """

        async def text_gen():
            """Execute text_gen operation.

            Returns:
                The result of the operation.
            """
            yield "a"
            yield "b"

        class Stream:
            """Represents the Stream class."""

            text_stream = text_gen()

            async def get_final_message(self):
                """Execute get_final_message operation.

                Returns:
                    The result of the operation.
                """
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
