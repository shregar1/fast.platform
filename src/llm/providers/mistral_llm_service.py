"""Mistral via OpenAI-compatible chat completions."""

from __future__ import annotations

from typing import Optional

from llm.constants import MISTRAL_DEFAULT_BASE_URL

from .openai_llm_service import OpenAILLMService


class MistralLLMService(OpenAILLMService):
    """Mistral AI via the OpenAI-compatible ``/v1/chat/completions`` API."""

    def __init__(self, api_key: str, base_url: Optional[str], model: str) -> None:
        super().__init__(api_key, base_url or MISTRAL_DEFAULT_BASE_URL, model)


__all__ = ["MistralLLMService"]
