"""Market / streams fanout configuration DTO."""

from __future__ import annotations

from ..constants import DEFAULT_HOST
from pydantic import ConfigDict

from .abstraction import IDTO


class StreamsConfigurationDTO(IDTO):
    """Represents the StreamsConfigurationDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = True
    tick_history: int = 1000
    fanout_queue_backend: str = ""
    backpressure_mode: str = "drop_oldest"
