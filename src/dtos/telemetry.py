"""OpenTelemetry / OTLP configuration DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class TelemetryConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    service_name: str = "fastmvc"
    exporter: str = "otlp"
    otlp_endpoint: str = ""
