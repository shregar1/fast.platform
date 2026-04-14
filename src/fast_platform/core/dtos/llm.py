"""LLM providers configuration DTO."""

from __future__ import annotations

from ..constants import OPENAI_PROVIDER
from typing import Any

from pydantic import Field, model_validator

from .abstraction import IDTO


class LLMProviderBlock(IDTO):
    """OpenAI-compatible provider (OpenAI, Groq, Mistral API, etc.)."""

    enabled: bool = False
    api_key: str = ""
    base_url: str | None = None
    model: str = ""


class OllamaProviderBlock(IDTO):
    """Represents the OllamaProviderBlock class."""

    enabled: bool = False
    base_url: str = "http://localhost:11434"
    model: str = ""


class GeminiProviderBlock(IDTO):
    """Google Gemini (``google-generativeai``); ``api_key`` is the Google AI Studio key."""

    enabled: bool = False
    api_key: str = ""
    model: str = ""
    base_url: str | None = None


class LLMConfigurationDTO(IDTO):
    """Represents the LLMConfigurationDTO class."""

    default_provider: str = OPENAI_PROVIDER

    openai: LLMProviderBlock = Field(default_factory=LLMProviderBlock)
    anthropic: LLMProviderBlock = Field(default_factory=LLMProviderBlock)
    ollama: OllamaProviderBlock = Field(default_factory=OllamaProviderBlock)
    groq: LLMProviderBlock = Field(default_factory=LLMProviderBlock)
    mistral: LLMProviderBlock = Field(default_factory=LLMProviderBlock)
    gemini: GeminiProviderBlock = Field(default_factory=GeminiProviderBlock)

    # Legacy flat keys (merged into nested blocks before validation)
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    @model_validator(mode="before")
    @classmethod
    def _merge_legacy_flat_keys(cls, data: Any) -> Any:
        """Execute _merge_legacy_flat_keys operation.

        Args:
            data: The data parameter.

        Returns:
            The result of the operation.
        """
        if not isinstance(data, dict):
            return data
        d = dict(data)

        def as_dict(key: str) -> dict[str, Any]:
            """Execute as_dict operation.

            Args:
                key: The key parameter.

            Returns:
                The result of the operation.
            """
            v = d.get(key)
            return dict(v) if isinstance(v, dict) else {}

        oa = as_dict(OPENAI_PROVIDER)
        if d.get("openai_api_key"):
            oa.setdefault("api_key", d["openai_api_key"])
            oa.setdefault("enabled", True)
        d[OPENAI_PROVIDER] = oa

        an = as_dict("anthropic")
        if d.get("anthropic_api_key"):
            an.setdefault("api_key", d["anthropic_api_key"])
            an.setdefault("enabled", True)
        d["anthropic"] = an

        ol = as_dict("ollama")
        if d.get("ollama_base_url") and d["ollama_base_url"] != "http://localhost:11434":
            ol.setdefault("base_url", d["ollama_base_url"])
            ol.setdefault("enabled", True)
        d["ollama"] = ol

        return d
