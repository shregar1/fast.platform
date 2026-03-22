"""Scheduler jobs subsection DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class SchedulerJobsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
