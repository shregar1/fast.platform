"""Singleton accessor for identity providers configuration."""

from __future__ import annotations

from ..constants import DEFAULT_HOST
from typing import Optional, Type

from ..dtos import IdentityProvidersConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class IdentityProvidersConfiguration(ConfigurationSingletonBase[IdentityProvidersConfigurationDTO]):
    """Represents the IdentityProvidersConfiguration class."""

    _instance: Optional["IdentityProvidersConfiguration"] = None
    _section: str = "identity"
    _env_key: str = "IDENTITY"
    _dto: Type[IdentityProvidersConfigurationDTO] = IdentityProvidersConfigurationDTO
