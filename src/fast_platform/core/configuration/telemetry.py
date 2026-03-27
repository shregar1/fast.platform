"""Singleton accessor for telemetry configuration."""

from __future__ import annotations

from typing import Optional, Type

from ..dtos import TelemetryConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class TelemetryConfiguration(ConfigurationSingletonBase[TelemetryConfigurationDTO]):
    """Represents the TelemetryConfiguration class."""

    _instance: Optional["TelemetryConfiguration"] = None
    _section: str = "telemetry"
    _env_key: str = "TELEMETRY"
    _dto: Type[TelemetryConfigurationDTO] = TelemetryConfigurationDTO
