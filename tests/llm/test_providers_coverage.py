"""Cover providers.py with mocks (no real API calls)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_openai_generate() -> None:
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content="hello"))]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
    with patch("openai.AsyncOpenAI", return_value=mock_client):
        from fast_llm.providers import OpenAILLMService

        svc = OpenAILLMService("k", None, "m")
        assert await svc.generate("p", max_tokens=10) == "hello"


@pytest.mark.asyncio
async def test_anthropic_generate_text_parts() -> None:
    t1 = SimpleNamespace(type="text", text="a")
    t2 = SimpleNamespace(type="image", text="x")
    mock_resp = MagicMock(content=[t1, t2])
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_resp)
    with patch("anthropic.AsyncAnthropic", return_value=mock_client):
        from fast_llm.providers import AnthropicLLMService

        svc = AnthropicLLMService("k", "http://localhost", "claude")
        assert await svc.generate("p") == "a"


@pytest.mark.asyncio
async def test_anthropic_base_url_optional() -> None:
    mock_resp = MagicMock(content=[])
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_resp)
    with patch("anthropic.AsyncAnthropic", return_value=mock_client):
        from fast_llm.providers import AnthropicLLMService

        svc = AnthropicLLMService("k", None, "claude")
        assert await svc.generate("p") == ""


@pytest.mark.asyncio
async def test_ollama_generate() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json = MagicMock(return_value={"message": {"content": "ollama-out"}})
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_cm)
    mock_cm.__aexit__ = AsyncMock(return_value=None)
    mock_cm.post = AsyncMock(return_value=mock_response)
    mock_async_client = MagicMock(return_value=mock_cm)
    with patch("httpx.AsyncClient", mock_async_client):
        from fast_llm.providers import OllamaLLMService

        svc = OllamaLLMService("http://127.0.0.1:11434", "llama")
        assert await svc.generate("hi") == "ollama-out"


def test_build_llm_service_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    from fast_llm import providers as prov

    class O:
        enabled = True
        api_key = "k"
        base_url = None
        model = "gpt"

    class Cfg:
        openai = O()
        anthropic = SimpleNamespace(enabled=False)
        ollama = SimpleNamespace(enabled=False)

    class LLMConfiguration:
        def get_config(self):
            return Cfg()

    monkeypatch.setattr(prov, "LLMConfiguration", LLMConfiguration)
    svc = prov.build_llm_service("openai")
    assert svc is not None
    assert prov.build_llm_service("anthropic") is None
    assert prov.build_llm_service("ollama") is None


def test_build_llm_service_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    from fast_llm import providers as prov

    class Cfg:
        openai = SimpleNamespace(enabled=False)
        anthropic = SimpleNamespace(enabled=True, api_key="a", base_url=None, model="c")
        ollama = SimpleNamespace(enabled=False)

    class LLMConfiguration:
        def get_config(self):
            return Cfg()

    monkeypatch.setattr(prov, "LLMConfiguration", LLMConfiguration)
    svc = prov.build_llm_service("anthropic")
    assert svc is not None


def test_build_llm_service_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    from fast_llm import providers as prov

    class Cfg:
        openai = SimpleNamespace(enabled=False)
        anthropic = SimpleNamespace(enabled=False)
        ollama = SimpleNamespace(enabled=True, base_url="http://x", model="m")

    class LLMConfiguration:
        def get_config(self):
            return Cfg()

    monkeypatch.setattr(prov, "LLMConfiguration", LLMConfiguration)
    svc = prov.build_llm_service("ollama")
    assert svc is not None


def test_illm_service_protocol() -> None:
    from fast_llm.providers import ILLMService, OpenAILLMService

    with patch("openai.AsyncOpenAI", return_value=MagicMock()):
        s = OpenAILLMService("k", None, "m")
        assert isinstance(s, ILLMService)
