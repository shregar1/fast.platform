"""Celery jobs subsection DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class CeleryJobsDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    broker_url: str = ""
    result_backend: str = ""
    namespace: str = ""
