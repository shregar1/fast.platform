"""Mistral via OpenAI-compatible chat completions."""

from __future__ import annotations

from typing import Optional

from integrations.llm.constants import MISTRAL_DEFAULT_BASE_URL

from .openai_llm_service import OpenAILLMService


class MistralLLMService(OpenAILLMService):
    """Mistral AI via the OpenAI-compatible ``/v1/chat/completions`` API."""

    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            base_url: The base_url parameter.
            model: The model parameter.
        """
        super().__init__(api_key, base_url or MISTRAL_DEFAULT_BASE_URL, model)


__all__ = ["MistralLLMService"]
