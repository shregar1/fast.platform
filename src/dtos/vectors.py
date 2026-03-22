"""Vector stores configuration DTO."""

from __future__ import annotations

from pydantic import ConfigDict, Field

from .abstraction import IDTO
from .pinecone_config import PineconeConfigDTO
from .qdrant_config import QdrantConfigDTO
from .weaviate_config import WeaviateConfigDTO


class VectorsConfigurationDTO(IDTO):
    model_config = ConfigDict(extra="ignore")
    pinecone: PineconeConfigDTO = Field(default_factory=PineconeConfigDTO)
    qdrant: QdrantConfigDTO = Field(default_factory=QdrantConfigDTO)
    weaviate: WeaviateConfigDTO = Field(default_factory=WeaviateConfigDTO)
