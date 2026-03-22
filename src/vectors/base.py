"""
Vector store interface and factory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from fast_core import VectorsConfiguration


class IVectorStore(ABC):
    """Interface for vector stores (Pinecone, Qdrant, Weaviate)."""

    name: str

    @abstractmethod
    def upsert(self, index_name: str, vectors: List[tuple[str, List[float], Optional[dict[str, Any]]]]) -> None:
        """Upsert vectors (id, vector, metadata)."""
        raise NotImplementedError

    @abstractmethod
    def query(
        self,
        index_name: str,
        vector: List[float],
        *,
        top_k: int = 10,
        filter: Optional[dict[str, Any]] = None,
    ) -> List[tuple[str, float, Optional[dict[str, Any]]]]:
        """Query by vector; return list of (id, score, metadata)."""
        raise NotImplementedError

    @abstractmethod
    def delete_index(self, index_name: str) -> None:
        """Delete an index/namespace."""
        raise NotImplementedError


def build_vector_store(backend: str = "pinecone") -> Optional[IVectorStore]:
    """
    Build a vector store from VectorsConfiguration (config/vectors/config.json).
    backend: "pinecone" | "qdrant" | "weaviate"
    """
    cfg = VectorsConfiguration().get_config()

    if backend == "pinecone" and getattr(cfg.pinecone, "enabled", False) and cfg.pinecone.api_key:
        try:
            from .pinecone_backend import PineconeVectorStore
            return PineconeVectorStore(
                api_key=cfg.pinecone.api_key,
                environment=cfg.pinecone.environment,
                index_name=cfg.pinecone.index_name,
            )
        except ImportError:
            return None

    if backend == "qdrant" and getattr(cfg.qdrant, "enabled", False) and cfg.qdrant.url:
        try:
            from .qdrant_backend import QdrantVectorStore
            return QdrantVectorStore(
                url=cfg.qdrant.url,
                api_key=cfg.qdrant.api_key,
            )
        except ImportError:
            return None

    if backend == "weaviate" and getattr(cfg.weaviate, "enabled", False) and cfg.weaviate.url:
        try:
            from .weaviate_backend import WeaviateVectorStore
            return WeaviateVectorStore(
                url=cfg.weaviate.url,
                api_key=cfg.weaviate.api_key,
            )
        except ImportError:
            return None

    return None
