"""Singleton accessor for realtime (WebRTC) configuration."""

from __future__ import annotations

from typing import Optional, Type

from ..dtos import RealtimeConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class RealtimeConfiguration(ConfigurationSingletonBase[RealtimeConfigurationDTO]):
    """Represents the RealtimeConfiguration class."""

    _instance: Optional["RealtimeConfiguration"] = None
    _section: str = "realtime"
    _env_key: str = "REALTIME"
    _dto: Type[RealtimeConfigurationDTO] = RealtimeConfigurationDTO
