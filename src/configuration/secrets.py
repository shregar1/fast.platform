"""Singleton accessor for secrets configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import SecretsConfigurationDTO
from .abstraction import IConfiguration


class SecretsConfiguration(IConfiguration[SecretsConfigurationDTO]):
    _instance: Optional["SecretsConfiguration"] = None
    _section: str = "secrets"
    _env_key: str = "SECRETS"
    _dto: Type[SecretsConfigurationDTO] = SecretsConfigurationDTO
