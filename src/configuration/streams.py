"""Singleton accessor for streams configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import StreamsConfigurationDTO
from .abstraction import IConfiguration


class StreamsConfiguration(IConfiguration[StreamsConfigurationDTO]):
    _instance: Optional["StreamsConfiguration"] = None
    _section: str = "streams"
    _env_key: str = "STREAMS"
    _dto: Type[StreamsConfigurationDTO] = StreamsConfigurationDTO
