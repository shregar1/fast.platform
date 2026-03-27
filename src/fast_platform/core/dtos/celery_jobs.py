"""Celery jobs subsection DTO."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class CeleryJobsDTO(IDTO):
    """Represents the CeleryJobsDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    broker_url: str = ""
    result_backend: str = ""
    namespace: str = ""
