"""Sentry configuration DTO."""

from __future__ import annotations

from typing import Optional

from .abstraction import IDTO


class SentryConfigurationDTO(IDTO):
    """Represents the SentryConfigurationDTO class."""

    dsn: Optional[str] = None
    environment: str = "production"
    release: Optional[str] = None
    traces_sample_rate: float = 0.1
    profiles_sample_rate: float = 0.1
    debug: bool = False
    enabled: bool = False
