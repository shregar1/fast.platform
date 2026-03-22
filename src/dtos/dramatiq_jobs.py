"""Dramatiq jobs subsection DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class DramatiqJobsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    broker_url: str = ""
    queue_name: str = "default"
