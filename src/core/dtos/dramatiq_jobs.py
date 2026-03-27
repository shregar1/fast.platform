"""Dramatiq jobs subsection DTO."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class DramatiqJobsDTO(IDTO):
    """Represents the DramatiqJobsDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    broker_url: str = ""
    queue_name: str = "default"
