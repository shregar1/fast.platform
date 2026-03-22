"""Singleton accessor for DB configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import DBConfigurationDTO
from .abstraction import IConfiguration


class DBConfiguration(IConfiguration[DBConfigurationDTO]):
    _instance: Optional["DBConfiguration"] = None
    _section: str = "db"
    _env_key: str = "DB"
    _dto: Type[DBConfigurationDTO] = DBConfigurationDTO
