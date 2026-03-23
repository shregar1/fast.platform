"""OpenTelemetry / OTLP configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class TelemetryConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    service_name: str = "fastmvc"
    exporter: str = "otlp"
    otlp_endpoint: str = ""
