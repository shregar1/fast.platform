"""Singleton accessor for queues configuration."""

from __future__ import annotations

from ..constants import DEFAULT_HOST
from typing import Optional, Type

from ..dtos import QueuesConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class QueuesConfiguration(ConfigurationSingletonBase[QueuesConfigurationDTO]):
    """Represents the QueuesConfiguration class."""

    _instance: Optional["QueuesConfiguration"] = None
    _section: str = "queues"
    _env_key: str = "QUEUES"
    _dto: Type[QueuesConfigurationDTO] = QueuesConfigurationDTO
