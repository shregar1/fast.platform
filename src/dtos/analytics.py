"""Analytics configuration DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict, Field

from .http_sink import HttpSinkDTO


class AnalyticsConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    http_sink: HttpSinkDTO = Field(default_factory=HttpSinkDTO)
