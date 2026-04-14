"""Singleton accessor for MongoDB configuration."""

from __future__ import annotations

from ..constants import DEFAULT_HOST
from typing import Optional, Type

from ..dtos.mongodb import MongoDBConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class MongoDBConfiguration(ConfigurationSingletonBase[MongoDBConfigurationDTO]):
    """Represents the MongoDBConfiguration class."""

    _instance: Optional["MongoDBConfiguration"] = None
    _section: str = "mongodb"
    _env_key: str = "MONGODB"
    _dto: Type[MongoDBConfigurationDTO] = MongoDBConfigurationDTO
