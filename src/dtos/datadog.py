"""Datadog configuration DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class DatadogConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    api_key: str = ""
    site: str = "datadoghq.com"
