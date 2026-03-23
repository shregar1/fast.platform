"""Weaviate vector store subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class WeaviateConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    api_key: str = ""
