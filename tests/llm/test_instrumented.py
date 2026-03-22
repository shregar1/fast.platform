"""Instrumented LLM services (requires openai / anthropic SDKs for full tests)."""

from __future__ import annotations

import types
from typing import Any, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("openai")


@pytest.mark.asyncio
async def test_instrumented_openai_emits_usage() -> None:
    from llm.instrumented import InstrumentedOpenAILLMService
    from llm.token_usage import TokenUsage

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
    ) -> None:
        self._model = model
        self._client = mock_client
        self._on_token_usage = on_token_usage

    with patch.object(InstrumentedOpenAILLMService, "__init__", fake_init):
        svc = InstrumentedOpenAILLMService("k", None, "m", on_token_usage=cb)
        out = await svc.generate("hi", max_tokens=10)
        assert out == "ok"
        assert len(received) == 1
        assert received[0].total_tokens == 3
