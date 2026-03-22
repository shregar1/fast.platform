"""Market / streams fanout configuration DTO."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class StreamsConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = True
    tick_history: int = 1000
    fanout_queue_backend: str = ""
    backpressure_mode: str = "drop_oldest"
