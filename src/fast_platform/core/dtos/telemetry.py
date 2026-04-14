"""OpenTelemetry / OTLP configuration DTO."""

from __future__ import annotations

from ..constants import SERVICE_NAME
from pydantic import ConfigDict

from .abstraction import IDTO


class TelemetryConfigurationDTO(IDTO):
    """Represents the TelemetryConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    service_name: str = SERVICE_NAME
    exporter: str = "otlp"
    otlp_endpoint: str = ""
