"""Singleton accessor for DB configuration."""

from __future__ import annotations

from ..constants import DEFAULT_SQLITE_URL_PREFIX
from typing import Optional, Type

from ..dtos import DBConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class DBConfiguration(ConfigurationSingletonBase[DBConfigurationDTO]):
    """Represents the DBConfiguration class."""

    _instance: Optional["DBConfiguration"] = None
    _section: str = "db"
    _env_key: str = "DB"
    _dto: Type[DBConfigurationDTO] = DBConfigurationDTO
