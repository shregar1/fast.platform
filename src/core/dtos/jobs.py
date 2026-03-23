"""Aggregate jobs configuration DTO."""

from __future__ import annotations

from typing import Dict

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .celery_jobs import CeleryJobsDTO
from .dramatiq_jobs import DramatiqJobsDTO
from .rq_jobs import RqJobsDTO
from .scheduler_jobs import SchedulerJobsDTO


class JobsConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    celery: CeleryJobsDTO = Field(default_factory=CeleryJobsDTO)
    rq: RqJobsDTO = Field(default_factory=RqJobsDTO)
    dramatiq: DramatiqJobsDTO = Field(default_factory=DramatiqJobsDTO)
    scheduler: SchedulerJobsDTO = Field(default_factory=SchedulerJobsDTO)
    queue_timeouts: Dict[str, int] = Field(default_factory=dict)
