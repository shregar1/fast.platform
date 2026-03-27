"""Datadog configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class DatadogConfigurationDTO(IDTO):
    """Represents the DatadogConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    api_key: str = ""
    site: str = "datadoghq.com"
