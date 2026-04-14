"""Scheduler jobs subsection DTO."""

from __future__ import annotations

from ..constants import DEFAULT_TIMEOUT_SECONDS
from pydantic import ConfigDict

from .abstraction import IDTO


class SchedulerJobsDTO(IDTO):
    """Represents the SchedulerJobsDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
