"""Singleton accessor for streams configuration."""

from __future__ import annotations

from typing import Optional, Type

from core.dtos import StreamsConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class StreamsConfiguration(ConfigurationSingletonBase[StreamsConfigurationDTO]):
    _instance: Optional["StreamsConfiguration"] = None
    _section: str = "streams"
    _env_key: str = "STREAMS"
    _dto: Type[StreamsConfigurationDTO] = StreamsConfigurationDTO
