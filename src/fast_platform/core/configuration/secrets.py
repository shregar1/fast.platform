"""Singleton accessor for secrets configuration."""

from __future__ import annotations

from typing import Optional, Type

from ..dtos import SecretsConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class SecretsConfiguration(ConfigurationSingletonBase[SecretsConfigurationDTO]):
    """Represents the SecretsConfiguration class."""

    _instance: Optional["SecretsConfiguration"] = None
    _section: str = "secrets"
    _env_key: str = "SECRETS"
    _dto: Type[SecretsConfigurationDTO] = SecretsConfigurationDTO
