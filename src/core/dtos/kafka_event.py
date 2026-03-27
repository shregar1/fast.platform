"""Kafka events subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class KafkaEventDTO(IDTO):
    """Represents the KafkaEventDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    topic: str = ""
