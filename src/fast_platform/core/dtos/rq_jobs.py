"""RQ jobs subsection DTO."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class RqJobsDTO(IDTO):
    """Represents the RqJobsDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    connection_url: str = ""
    redis_url: str = ""
    queue_name: str = "default"
