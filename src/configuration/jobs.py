"""Singleton accessor for jobs configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import JobsConfigurationDTO
from .abstraction import IConfiguration


class JobsConfiguration(IConfiguration[JobsConfigurationDTO]):
    _instance: Optional["JobsConfiguration"] = None
    _section: str = "jobs"
    _env_key: str = "JOBS"
    _dto: Type[JobsConfigurationDTO] = JobsConfigurationDTO
