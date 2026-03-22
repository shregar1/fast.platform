"""Singleton accessor for identity providers configuration."""

from __future__ import annotations

from typing import Optional, Type

from dtos import IdentityProvidersConfigurationDTO
from .abstraction import IConfiguration


class IdentityProvidersConfiguration(IConfiguration[IdentityProvidersConfigurationDTO]):
    _instance: Optional["IdentityProvidersConfiguration"] = None
    _section: str = "identity"
    _env_key: str = "IDENTITY"
    _dto: Type[IdentityProvidersConfigurationDTO] = IdentityProvidersConfigurationDTO