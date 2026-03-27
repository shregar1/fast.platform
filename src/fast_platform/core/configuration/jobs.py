"""Singleton accessor for jobs configuration."""

from __future__ import annotations

from typing import Optional, Type

from core.dtos import JobsConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class JobsConfiguration(ConfigurationSingletonBase[JobsConfigurationDTO]):
    """Represents the JobsConfiguration class."""

    _instance: Optional["JobsConfiguration"] = None
    _section: str = "jobs"
    _env_key: str = "JOBS"
    _dto: Type[JobsConfigurationDTO] = JobsConfigurationDTO
