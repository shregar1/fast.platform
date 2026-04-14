"""Singleton accessor for cache configuration."""

from __future__ import annotations

from ..constants import DEFAULT_REDIS_URL
from typing import Optional, Type

from ..dtos import CacheConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class CacheConfiguration(ConfigurationSingletonBase[CacheConfigurationDTO]):
    """Represents the CacheConfiguration class."""

    _instance: Optional["CacheConfiguration"] = None
    _section: str = "cache"
    _env_key: str = "CACHE"
    _dto: Type[CacheConfigurationDTO] = CacheConfigurationDTO
