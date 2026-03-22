"""Singleton accessor for storage configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import StorageConfigurationDTO
from .abstraction import IConfiguration


class StorageConfiguration(IConfiguration[StorageConfigurationDTO]):
    _instance: Optional["StorageConfiguration"] = None
    _section: str = "storage"
    _env_key: str = "STORAGE"
    _dto: Type[StorageConfigurationDTO] = StorageConfigurationDTO
