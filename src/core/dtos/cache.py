"""Cache configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class CacheConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    backend: str = "memory"
    default_ttl_seconds: int = 300
    redis_url: str = ""
    namespace: str = "app"
