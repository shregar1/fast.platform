"""HTTP sink for analytics subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class HttpSinkDTO(IDTO):
    """Represents the HttpSinkDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    endpoint: str = ""
    api_key: str = ""
