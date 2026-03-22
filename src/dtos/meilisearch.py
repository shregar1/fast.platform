"""Meilisearch search backend subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class MeilisearchDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    host: str = ""
    api_key: str = ""
