"""Cache configuration DTO."""

from __future__ import annotations

from ..constants import DEFAULT_REDIS_URL
from pydantic import ConfigDict

from .abstraction import IDTO


class CacheConfigurationDTO(IDTO):
    """Represents the CacheConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    backend: str = "memory"
    default_ttl_seconds: int = 300
    redis_url: str = ""
    namespace: str = "app"
