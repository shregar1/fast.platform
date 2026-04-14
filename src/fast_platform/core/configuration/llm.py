"""Singleton accessor for LLM configuration."""

from __future__ import annotations

from ..constants import OPENAI_PROVIDER, OLLAMA_DEFAULT_BASE_URL
from typing import Optional, Type

from ..dtos import LLMConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class LLMConfiguration(ConfigurationSingletonBase[LLMConfigurationDTO]):
    """Represents the LLMConfiguration class."""

    _instance: Optional["LLMConfiguration"] = None
    _section: str = "llm"
    _env_key: str = "LLM"
    _dto: Type[LLMConfigurationDTO] = LLMConfigurationDTO
