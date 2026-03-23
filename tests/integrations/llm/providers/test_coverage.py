from __future__ import annotations

"""Cover :mod:`integrations.llm.providers` with mocks (no real API calls).

Mirrors ``src/llm/providers/`` under ``tests/llm/providers/``.
"""
import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integrations.llm.providers.abstraction import ILLMProvidersTests


class TestProvidersCoverage(ILLMProvidersTests):
    @pytest.mark.asyncio
    async def test_openai_generate(self) -> None:
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content="hello"))]
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
        with patch("openai.AsyncOpenAI", return_value=mock_client):
            from integrations.llm.providers import OpenAILLMService

            svc = OpenAILLMService("k", None, "m")
            assert await svc.generate("p", max_tokens=10) == "hello"

    @pytest.mark.asyncio
    async def test_anthropic_generate_text_parts(self) -> None:
        t1 = SimpleNamespace(type="text", text="a")
        t2 = SimpleNamespace(type="image", text="x")
        mock_resp = MagicMock(content=[t1, t2])
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_resp)
        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            from integrations.llm.providers import AnthropicLLMService

            svc = AnthropicLLMService("k", "http://localhost", "claude")
            assert await svc.generate("p") == "a"

    @pytest.mark.asyncio
    async def test_anthropic_base_url_optional(self) -> None:
        mock_resp = MagicMock(content=[])
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_resp)
        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            from integrations.llm.providers import AnthropicLLMService

            svc = AnthropicLLMService("k", None, "claude")
            assert await svc.generate("p") == ""

    @pytest.mark.asyncio
    async def test_ollama_generate(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = MagicMock(return_value={"message": {"content": "ollama-out"}})
        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_cm)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_cm.post = AsyncMock(return_value=mock_response)
        mock_async_client = MagicMock(return_value=mock_cm)
        with patch("httpx.AsyncClient", mock_async_client):
            from integrations.llm.providers import OllamaLLMService

            svc = OllamaLLMService("http://127.0.0.1:11434", "llama")
            assert await svc.generate("hi") == "ollama-out"

    def test_build_llm_service_openai(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from integrations.llm import providers as prov

        class OpenAIStub:
            enabled = True
            api_key = "k"
            base_url = None
            model = "gpt"

        class Cfg:
            openai = OpenAIStub()
            anthropic = SimpleNamespace(enabled=False)
            ollama = SimpleNamespace(enabled=False)
            groq = SimpleNamespace(enabled=False)
            mistral = SimpleNamespace(enabled=False)
            gemini = SimpleNamespace(enabled=False)

        class LLMConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("integrations.llm.providers.factory.LLMConfiguration", LLMConfiguration)
        svc = prov.build_llm_service("openai")
        assert svc is not None
        assert prov.build_llm_service("anthropic") is None
        assert prov.build_llm_service("ollama") is None

    def test_build_llm_service_anthropic(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from integrations.llm import providers as prov

        class Cfg:
            openai = SimpleNamespace(enabled=False)
            anthropic = SimpleNamespace(enabled=True, api_key="a", base_url=None, model="c")
            ollama = SimpleNamespace(enabled=False)
            groq = SimpleNamespace(enabled=False)
            mistral = SimpleNamespace(enabled=False)
            gemini = SimpleNamespace(enabled=False)

        class LLMConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("integrations.llm.providers.factory.LLMConfiguration", LLMConfiguration)
        svc = prov.build_llm_service("anthropic")
        assert svc is not None

    def test_build_llm_service_ollama(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from integrations.llm import providers as prov

        class Cfg:
            openai = SimpleNamespace(enabled=False)
            anthropic = SimpleNamespace(enabled=False)
            ollama = SimpleNamespace(enabled=True, base_url="http://x", model="m")
            groq = SimpleNamespace(enabled=False)
            mistral = SimpleNamespace(enabled=False)
            gemini = SimpleNamespace(enabled=False)

        class LLMConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("integrations.llm.providers.factory.LLMConfiguration", LLMConfiguration)
        svc = prov.build_llm_service("ollama")
        assert svc is not None

    def test_illm_service_protocol(self) -> None:
        from integrations.llm.providers import ILLMService, OpenAILLMService

        with patch("openai.AsyncOpenAI", return_value=MagicMock()):
            s = OpenAILLMService("k", None, "m")
            assert isinstance(s, ILLMService)

    @pytest.mark.asyncio
    async def test_groq_generate(self) -> None:
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content="groq"))]
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
        with patch("openai.AsyncOpenAI", return_value=mock_client):
            from integrations.llm.providers import GroqLLMService

            svc = GroqLLMService("k", None, "llama-3")
            assert await svc.generate("p") == "groq"

    @pytest.mark.asyncio
    async def test_mistral_generate(self) -> None:
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content="mistral-out"))]
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
        with patch("openai.AsyncOpenAI", return_value=mock_client):
            from integrations.llm.providers import MistralLLMService

            svc = MistralLLMService("k", None, "mistral-small")
            assert await svc.generate("p") == "mistral-out"

    @pytest.mark.asyncio
    async def test_gemini_generate(self) -> None:
        mock_resp = MagicMock()
        mock_resp.text = "gemini-text"
        mock_model = MagicMock()
        mock_model.generate_content_async = AsyncMock(return_value=mock_resp)
        mock_genai = types.ModuleType("google.generativeai")
        mock_genai.configure = MagicMock()
        mock_genai.GenerativeModel = MagicMock(return_value=mock_model)
        mock_genai.GenerationConfig = MagicMock(return_value=MagicMock())
        old_google = sys.modules.get("google")
        old_genai = sys.modules.get("google.generativeai")
        sys.modules.setdefault("google", types.ModuleType("google"))
        sys.modules["google.generativeai"] = mock_genai
        try:
            from integrations.llm.providers import GeminiLLMService

            svc = GeminiLLMService("k", "gemini-1.5-flash")
            assert await svc.generate("hi") == "gemini-text"
        finally:
            if old_genai is not None:
                sys.modules["google.generativeai"] = old_genai
            elif "google.generativeai" in sys.modules:
                del sys.modules["google.generativeai"]
            if old_google is None and "google" in sys.modules:
                del sys.modules["google"]

    def test_build_llm_service_groq(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from integrations.llm import providers as prov

        class Cfg:
            openai = SimpleNamespace(enabled=False)
            anthropic = SimpleNamespace(enabled=False)
            ollama = SimpleNamespace(enabled=False)
            groq = SimpleNamespace(enabled=True, api_key="g", base_url=None, model="llama-3")
            mistral = SimpleNamespace(enabled=False)
            gemini = SimpleNamespace(enabled=False)

        class LLMConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("integrations.llm.providers.factory.LLMConfiguration", LLMConfiguration)
        assert prov.build_llm_service("groq") is not None

    def test_build_llm_service_mistral(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from integrations.llm import providers as prov

        class Cfg:
            openai = SimpleNamespace(enabled=False)
            anthropic = SimpleNamespace(enabled=False)
            ollama = SimpleNamespace(enabled=False)
            groq = SimpleNamespace(enabled=False)
            mistral = SimpleNamespace(
                enabled=True, api_key="m", base_url=None, model="mistral-small"
            )
            gemini = SimpleNamespace(enabled=False)

        class LLMConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("integrations.llm.providers.factory.LLMConfiguration", LLMConfiguration)
        assert prov.build_llm_service("mistral") is not None

    def test_build_llm_service_gemini(self, monkeypatch: pytest.MonkeyPatch) -> None:
        pytest.importorskip("google.generativeai")

        from integrations.llm import providers as prov

        class Cfg:
            openai = SimpleNamespace(enabled=False)
            anthropic = SimpleNamespace(enabled=False)
            ollama = SimpleNamespace(enabled=False)
            groq = SimpleNamespace(enabled=False)
            mistral = SimpleNamespace(enabled=False)
            gemini = SimpleNamespace(enabled=True, api_key="g", model="gemini-pro", base_url=None)

        class LLMConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("integrations.llm.providers.factory.LLMConfiguration", LLMConfiguration)
        assert prov.build_llm_service("gemini") is not None
