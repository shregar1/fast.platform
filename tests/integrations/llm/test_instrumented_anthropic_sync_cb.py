"""Module test_instrumented_anthropic_sync_cb.py."""

from __future__ import annotations

"""Instrumented Anthropic + sync token callback + _maybe_await path."""
import types
from typing import Any, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integrations.llm.abstraction import ILLMTests

pytest.importorskip("anthropic")


class TestInstrumentedAnthropicSyncCb(ILLMTests):
    """Represents the TestInstrumentedAnthropicSyncCb class."""

    @pytest.mark.asyncio
    async def test_instrumented_anthropic_emits_usage(self) -> None:
        """Execute test_instrumented_anthropic_emits_usage operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.integrations.llm.instrumented import InstrumentedAnthropicLLMService
        from fast_platform.integrations.llm.token_usage import TokenUsage

        usage_obj = types.SimpleNamespace(input_tokens=1, output_tokens=2)
        text_block = types.SimpleNamespace(type="text", text="ok")
        resp = types.SimpleNamespace(content=[text_block], usage=usage_obj)
        mock_create = AsyncMock(return_value=resp)
        mock_client = MagicMock()
        mock_client.messages.create = mock_create
        received: List[TokenUsage] = []

        def cb_sync(u: TokenUsage) -> None:
            """Execute cb_sync operation.

            Args:
                u: The u parameter.

            Returns:
                The result of the operation.
            """
            received.append(u)

        def fake_init(
            self: Any, api_key: str, base_url: Any, model: str, *, on_token_usage: Any = None
        ) -> None:
            """Execute fake_init operation.

            Args:
                api_key: The api_key parameter.
                base_url: The base_url parameter.
                model: The model parameter.
                on_token_usage: The on_token_usage parameter.

            Returns:
                The result of the operation.
            """
            self._model = model
            self._client = mock_client
            self._on_token_usage = on_token_usage

        with patch.object(InstrumentedAnthropicLLMService, "__init__", fake_init):
            svc = InstrumentedAnthropicLLMService("k", None, "m", on_token_usage=cb_sync)
            out = await svc.generate("hi", max_tokens=10)
            assert out == "ok"
            assert len(received) == 1
            assert received[0].total_tokens == 3

    @pytest.mark.asyncio
    async def test_instrumented_openai_async_callback(self) -> None:
        """Execute test_instrumented_openai_async_callback operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.integrations.llm.instrumented import InstrumentedOpenAILLMService
        from fast_platform.integrations.llm.token_usage import TokenUsage

        usage_obj = types.SimpleNamespace(prompt_tokens=1, completion_tokens=1, total_tokens=2)
        msg = types.SimpleNamespace(content="x")
        choice = types.SimpleNamespace(message=msg)
        resp = types.SimpleNamespace(choices=[choice], usage=usage_obj)
        mock_create = AsyncMock(return_value=resp)
        mock_client = MagicMock()
        mock_client.chat.completions.create = mock_create
        received: List[TokenUsage] = []

        async def cb_async(u: TokenUsage) -> None:
            """Execute cb_async operation.

            Args:
                u: The u parameter.

            Returns:
                The result of the operation.
            """
            received.append(u)

        def fake_init(
            self: Any,
            api_key: str,
            base_url: Any,
            model: str,
            *,
            on_token_usage: Any = None,
            usage_provider: str = "openai",
        ) -> None:
            """Execute fake_init operation.

            Args:
                api_key: The api_key parameter.
                base_url: The base_url parameter.
                model: The model parameter.
                on_token_usage: The on_token_usage parameter.
                usage_provider: The usage_provider parameter.

            Returns:
                The result of the operation.
            """
            self._model = model
            self._client = mock_client
            self._on_token_usage = on_token_usage
            self._usage_provider = usage_provider

        with patch.object(InstrumentedOpenAILLMService, "__init__", fake_init):
            svc = InstrumentedOpenAILLMService("k", None, "m", on_token_usage=cb_async)
            await svc.generate("q")
            assert len(received) == 1
