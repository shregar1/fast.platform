from __future__ import annotations

"""Instrumented LLM services (requires openai / anthropic SDKs for full tests)."""
import types
from typing import Any, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integrations.llm.abstraction import ILLMTests

pytest.importorskip("openai")


class TestInstrumented(ILLMTests):
    @pytest.mark.asyncio
    async def test_instrumented_openai_emits_usage(self) -> None:
        from integrations.llm.instrumented import InstrumentedOpenAILLMService
        from integrations.llm.token_usage import TokenUsage

        usage_obj = types.SimpleNamespace(prompt_tokens=1, completion_tokens=2, total_tokens=3)
        msg = types.SimpleNamespace(content="ok")
        choice = types.SimpleNamespace(message=msg)
        resp = types.SimpleNamespace(choices=[choice], usage=usage_obj)
        mock_create = AsyncMock(return_value=resp)
        mock_client = MagicMock()
        mock_client.chat.completions.create = mock_create
        received: List[TokenUsage] = []

        async def cb(u: TokenUsage) -> None:
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
            self._model = model
            self._client = mock_client
            self._on_token_usage = on_token_usage
            self._usage_provider = usage_provider

        with patch.object(InstrumentedOpenAILLMService, "__init__", fake_init):
            svc = InstrumentedOpenAILLMService("k", None, "m", on_token_usage=cb)
            out = await svc.generate("hi", max_tokens=10)
            assert out == "ok"
            assert len(received) == 1
            assert received[0].total_tokens == 3
