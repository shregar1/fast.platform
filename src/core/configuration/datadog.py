"""Singleton accessor for Datadog configuration."""

from __future__ import annotations

from typing import Optional, Type

from core.dtos import DatadogConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class DatadogConfiguration(ConfigurationSingletonBase[DatadogConfigurationDTO]):
    _instance: Optional["DatadogConfiguration"] = None
    _section: str = "datadog"
    _env_key: str = "DATADOG"
    _dto: Type[DatadogConfigurationDTO] = DatadogConfigurationDTO
