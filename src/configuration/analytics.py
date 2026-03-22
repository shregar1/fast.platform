"""Singleton accessor for analytics configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import AnalyticsConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class AnalyticsConfiguration(ConfigurationSingletonBase[AnalyticsConfigurationDTO]):
    _instance: Optional["AnalyticsConfiguration"] = None
    _section: str = "analytics"
    _env_key: str = "ANALYTICS"
    _dto: Type[AnalyticsConfigurationDTO] = AnalyticsConfigurationDTO
