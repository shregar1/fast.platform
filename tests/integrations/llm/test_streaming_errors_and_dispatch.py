"""Module test_streaming_errors_and_dispatch.py."""

from __future__ import annotations

"""Streaming edge cases: TypeError, UnsupportedLLMProviderError, async get_final_message."""
import types
from typing import Any, cast

import pytest

from core.errors import UnsupportedLLMProviderError
from integrations.llm.streaming import iter_anthropic_message_stream, iter_llm_stream
from tests.integrations.llm.abstraction import ILLMTests


class TestStreamingErrorsAndDispatch(ILLMTests):
    """Represents the TestStreamingErrorsAndDispatch class."""

    @pytest.mark.asyncio
    async def test_anthropic_stream_missing_text_stream(self) -> None:
        """Execute test_anthropic_stream_missing_text_stream operation.

        Returns:
            The result of the operation.
        """

        class Bad:
            """Represents the Bad class."""

            pass

        with pytest.raises(TypeError, match="text_stream"):
            async for _ in iter_anthropic_message_stream(Bad()):
                pass

    @pytest.mark.asyncio
    async def test_iter_llm_stream_bad_provider(self) -> None:
        """Execute test_iter_llm_stream_bad_provider operation.

        Returns:
            The result of the operation.
        """

        async def empty():
            """Execute empty operation.

            Returns:
                The result of the operation.
            """
            if False:
                yield None

        with pytest.raises(UnsupportedLLMProviderError, match="Unsupported LLM provider"):
            async for _ in iter_llm_stream(cast(Any, "not-a-provider"), empty()):
                pass

    @pytest.mark.asyncio
    async def test_anthropic_get_final_message_awaitable(self) -> None:
        """Execute test_anthropic_get_final_message_awaitable operation.

        Returns:
            The result of the operation.
        """

        async def text_gen():
            """Execute text_gen operation.

            Returns:
                The result of the operation.
            """
            yield "z"

        class Stream:
            """Represents the Stream class."""

            text_stream = text_gen()

            async def get_final_message(self):
                """Execute get_final_message operation.

                Returns:
                    The result of the operation.
                """
                return types.SimpleNamespace(
                    usage=types.SimpleNamespace(input_tokens=1, output_tokens=1)
                )

        chunks = []
        async for c in iter_anthropic_message_stream(Stream()):
            chunks.append(c)
        assert chunks[-1].usage is not None

    @pytest.mark.asyncio
    async def test_anthropic_no_get_final_message(self) -> None:
        """Execute test_anthropic_no_get_final_message operation.

        Returns:
            The result of the operation.
        """

        async def text_gen():
            """Execute text_gen operation.

            Returns:
                The result of the operation.
            """
            yield "a"

        class Stream:
            """Represents the Stream class."""

            text_stream = text_gen()

        chunks = []
        async for c in iter_anthropic_message_stream(Stream()):
            chunks.append(c)
        assert len(chunks) == 1
        assert chunks[0].usage is None
