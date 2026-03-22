"""HTTP sink for analytics subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class HttpSinkDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    endpoint: str = ""
    api_key: str = ""
