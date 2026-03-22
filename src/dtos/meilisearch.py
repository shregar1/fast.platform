"""Meilisearch search backend subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class MeilisearchDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    host: str = ""
    api_key: str = ""
