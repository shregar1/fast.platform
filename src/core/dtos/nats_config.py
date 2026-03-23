"""NATS queue backend subsection."""

from __future__ import annotations

from typing import List

from pydantic import ConfigDict, Field

from .abstraction import IDTO


class NATSConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    servers: List[str] = Field(default_factory=list)
    subject: str = ""
