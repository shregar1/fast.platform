"""Pinecone vector store subsection."""

from __future__ import annotations

from .abstraction import IDTO

from pydantic import ConfigDict


class PineconeConfigDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    enabled: bool = False
    api_key: str = ""
    environment: str = ""
    index_name: str = ""
