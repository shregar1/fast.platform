"""Singleton accessor for search configuration."""

from __future__ import annotations

from typing import Optional, Type

from core.dtos import SearchConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class SearchConfiguration(ConfigurationSingletonBase[SearchConfigurationDTO]):
    """Represents the SearchConfiguration class."""

    _instance: Optional["SearchConfiguration"] = None
    _section: str = "search"
    _env_key: str = "SEARCH"
    _dto: Type[SearchConfigurationDTO] = SearchConfigurationDTO
