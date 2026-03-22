"""Singleton accessor for queues configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import QueuesConfigurationDTO
from .abstraction import IConfiguration


class QueuesConfiguration(IConfiguration[QueuesConfigurationDTO]):
    _instance: Optional["QueuesConfiguration"] = None
    _section: str = "queues"
    _env_key: str = "QUEUES"
    _dto: Type[QueuesConfigurationDTO] = QueuesConfigurationDTO