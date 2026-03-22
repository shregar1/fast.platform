"""Factory: build an LLM service from :class:`~fast_platform.LLMConfiguration`."""

from __future__ import annotations

from typing import Literal, Optional

from fast_platform import LLMConfiguration

from .anthropic_llm_service import AnthropicLLMService
from .gemini_llm_service import GeminiLLMService
from .groq_llm_service import GroqLLMService
from .illm_service import ILLMService
from .mistral_llm_service import MistralLLMService
from .ollama_llm_service import OllamaLLMService
from .openai_llm_service import OpenAILLMService


def build_llm_service(
    provider: Literal[
        "openai",
        "anthropic",
        "ollama",
        "groq",
        "mistral",
        "gemini",
    ] = "openai",
) -> Optional[ILLMService]:
    """Build a provider from :class:`LLMConfiguration` (``config/llm/config.json``)."""
    cfg = LLMConfiguration().get_config()
    if provider == "openai":
        o = cfg.openai
        if getattr(o, "enabled", False) and o.api_key and o.model:
            return OpenAILLMService(o.api_key, o.base_url, o.model)
    if provider == "anthropic":
        a = cfg.anthropic
        if getattr(a, "enabled", False) and a.api_key and a.model:
            return AnthropicLLMService(a.api_key, a.base_url, a.model)
    if provider == "ollama":
        ol = cfg.ollama
        if getattr(ol, "enabled", False) and ol.base_url and ol.model:
            return OllamaLLMService(ol.base_url, ol.model)
    if provider == "groq":
        g = cfg.groq
        if getattr(g, "enabled", False) and g.api_key and g.model:
            return GroqLLMService(g.api_key, g.base_url, g.model)
    if provider == "mistral":
        m = cfg.mistral
        if getattr(m, "enabled", False) and m.api_key and m.model:
            return MistralLLMService(m.api_key, m.base_url, m.model)
    if provider == "gemini":
        gm = cfg.gemini
        if getattr(gm, "enabled", False) and gm.api_key and gm.model:
            return GeminiLLMService(gm.api_key, gm.model, gm.base_url)
    return None


__all__ = ["build_llm_service"]
