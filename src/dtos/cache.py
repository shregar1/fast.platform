"""Cache configuration DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class CacheConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    backend: str = "memory"
    default_ttl_seconds: int = 300
    redis_url: str = ""
    namespace: str = "app"
