"""Groq via OpenAI-compatible endpoint."""

from __future__ import annotations

from typing import Optional

from fast_platform.integrations.llm.constants import GROQ_DEFAULT_BASE_URL

from .openai_llm_service import OpenAILLMService


class GroqLLMService(OpenAILLMService):
    """Groq chat completions via the OpenAI-compatible endpoint."""

    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            base_url: The base_url parameter.
            model: The model parameter.
        """
        super().__init__(api_key, base_url or GROQ_DEFAULT_BASE_URL, model)


__all__ = ["GroqLLMService"]
