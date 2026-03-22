"""Singleton accessor for LLM configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import LLMConfigurationDTO
from .abstraction import IConfiguration


class LLMConfiguration(IConfiguration[LLMConfigurationDTO]):
    _instance: Optional["LLMConfiguration"] = None
    _section: str = "llm"
    _env_key: str = "LLM"
    _dto: Type[LLMConfigurationDTO] = LLMConfigurationDTO
