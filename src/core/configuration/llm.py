"""Singleton accessor for LLM configuration."""

from __future__ import annotations

from typing import Optional, Type

from core.dtos import LLMConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class LLMConfiguration(ConfigurationSingletonBase[LLMConfigurationDTO]):
    _instance: Optional["LLMConfiguration"] = None
    _section: str = "llm"
    _env_key: str = "LLM"
    _dto: Type[LLMConfigurationDTO] = LLMConfigurationDTO
