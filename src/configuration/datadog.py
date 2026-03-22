"""Singleton accessor for Datadog configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import DatadogConfigurationDTO
from .abstraction import IConfiguration


class DatadogConfiguration(IConfiguration[DatadogConfigurationDTO]):
    _instance: Optional["DatadogConfiguration"] = None
    _section: str = "datadog"
    _env_key: str = "DATADOG"
    _dto: Type[DatadogConfigurationDTO] = DatadogConfigurationDTO
