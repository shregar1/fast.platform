"""RQ jobs subsection DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class RqJobsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_url: str = ""
    redis_url: str = ""
    queue_name: str = "default"
