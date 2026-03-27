"""Qdrant vector store subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class QdrantConfigDTO(IDTO):
    """Represents the QdrantConfigDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    url: str = ""
    api_key: str = ""
