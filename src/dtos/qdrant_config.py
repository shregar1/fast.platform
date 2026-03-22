"""Qdrant vector store subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class QdrantConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    api_key: str = ""
