"""Scheduler jobs subsection DTO."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class SchedulerJobsDTO(IDTO):
    """Represents the SchedulerJobsDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
