"""Kafka events subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class KafkaEventDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    topic: str = ""
