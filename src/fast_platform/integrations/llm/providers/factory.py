"""Factory: build an LLM service from :class:`~fast_platform.LLMConfiguration`."""

from __future__ import annotations

from ..constants import OPENAI_PROVIDER, ANTHROPIC_PROVIDER, GEMINI_PROVIDER, GROQ_PROVIDER, MISTRAL_PROVIDER, OLLAMA_PROVIDER
from typing import TYPE_CHECKING, Literal, Optional

from fast_platform import LLMConfiguration

from .anthropic_llm_service import AnthropicLLMService
from .gemini_llm_service import GeminiLLMService
from .groq_llm_service import GroqLLMService
from .mistral_llm_service import MistralLLMService
from .ollama_llm_service import OllamaLLMService
from .openai_llm_service import OpenAILLMService

if TYPE_CHECKING:
    from .illm_service import ILLMService


def build_llm_service(
    provider: Literal[
        OPENAI_PROVIDER,
        ANTHROPIC_PROVIDER,
        OLLAMA_PROVIDER,
        GROQ_PROVIDER,
        MISTRAL_PROVIDER,
        GEMINI_PROVIDER,
    ] = OPENAI_PROVIDER,
) -> Optional[ILLMService]:
    """Build a provider from :class:`LLMConfiguration` (``config/llm/config.json``)."""
    cfg = LLMConfiguration().get_config()
    if provider == OPENAI_PROVIDER:
        o = cfg.openai
        if getattr(o, "enabled", False) and o.api_key and o.model:
            return OpenAILLMService(o.api_key, o.base_url, o.model)
    if provider == ANTHROPIC_PROVIDER:
        a = cfg.anthropic
        if getattr(a, "enabled", False) and a.api_key and a.model:
            return AnthropicLLMService(a.api_key, a.base_url, a.model)
    if provider == OLLAMA_PROVIDER:
        ol = cfg.ollama
        if getattr(ol, "enabled", False) and ol.base_url and ol.model:
            return OllamaLLMService(ol.base_url, ol.model)
    if provider == GROQ_PROVIDER:
        g = cfg.groq
        if getattr(g, "enabled", False) and g.api_key and g.model:
            return GroqLLMService(g.api_key, g.base_url, g.model)
    if provider == MISTRAL_PROVIDER:
        m = cfg.mistral
        if getattr(m, "enabled", False) and m.api_key and m.model:
            return MistralLLMService(m.api_key, m.base_url, m.model)
    if provider == GEMINI_PROVIDER:
        gm = cfg.gemini
        if getattr(gm, "enabled", False) and gm.api_key and gm.model:
            return GeminiLLMService(gm.api_key, gm.model, gm.base_url)
    return None


__all__ = ["build_llm_service"]
