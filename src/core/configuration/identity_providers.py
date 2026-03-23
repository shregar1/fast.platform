"""Singleton accessor for identity providers configuration."""

from __future__ import annotations

from typing import Optional, Type

from core.dtos import IdentityProvidersConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class IdentityProvidersConfiguration(ConfigurationSingletonBase[IdentityProvidersConfigurationDTO]):
    _instance: Optional["IdentityProvidersConfiguration"] = None
    _section: str = "identity"
    _env_key: str = "IDENTITY"
    _dto: Type[IdentityProvidersConfigurationDTO] = IdentityProvidersConfigurationDTO
