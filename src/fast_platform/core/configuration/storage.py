"""Singleton accessor for storage configuration."""

from __future__ import annotations

from ..constants import DEFAULT_AWS_REGION
from typing import Optional, Type

from ..dtos import StorageConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class StorageConfiguration(ConfigurationSingletonBase[StorageConfigurationDTO]):
    """Represents the StorageConfiguration class."""

    _instance: Optional["StorageConfiguration"] = None
    _section: str = "storage"
    _env_key: str = "STORAGE"
    _dto: Type[StorageConfigurationDTO] = StorageConfigurationDTO
