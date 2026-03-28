"""Singleton accessor for Sentry configuration."""

from __future__ import annotations

from typing import Optional, Type

from ..dtos.sentry import SentryConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class SentryConfiguration(ConfigurationSingletonBase[SentryConfigurationDTO]):
    """Represents the SentryConfiguration class."""

    _instance: Optional["SentryConfiguration"] = None
    _section: str = "sentry"
    _env_key: str = "SENTRY"
    _dto: Type[SentryConfigurationDTO] = SentryConfigurationDTO
