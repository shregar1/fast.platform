"""Analytics configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .http_sink import HttpSinkDTO


class AnalyticsConfigurationDTO(IDTO):
    """Represents the AnalyticsConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    http_sink: HttpSinkDTO = Field(default_factory=HttpSinkDTO)
