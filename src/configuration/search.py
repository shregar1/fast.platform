"""Singleton accessor for search configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import SearchConfigurationDTO
from .abstraction import IConfiguration


class SearchConfiguration(IConfiguration[SearchConfigurationDTO]):
    _instance: Optional["SearchConfiguration"] = None
    _section: str = "search"
    _env_key: str = "SEARCH"
    _dto: Type[SearchConfigurationDTO] = SearchConfigurationDTO
