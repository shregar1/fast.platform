"""Pinecone vector store subsection."""

from __future__ import annotations

from pydantic import ConfigDict

from .abstraction import IDTO


class PineconeConfigDTO(IDTO):
    """Represents the PineconeConfigDTO class."""

    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    api_key: str = ""
    environment: str = ""
    index_name: str = ""
