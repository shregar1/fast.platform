"""Singleton accessor for email configuration."""

from __future__ import annotations

from typing import Optional, Type

from ..dtos.email import EmailConfigurationDTO

from .abstraction import ConfigurationSingletonBase


class EmailConfiguration(ConfigurationSingletonBase[EmailConfigurationDTO]):
    """Represents the EmailConfiguration class."""

    _instance: Optional["EmailConfiguration"] = None
    _section: str = "email"
    _env_key: str = "EMAIL"
    _dto: Type[EmailConfigurationDTO] = EmailConfigurationDTO
