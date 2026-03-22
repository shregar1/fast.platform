"""Qdrant vector store backend."""

from __future__ import annotations

from typing import Any, List, Optional

from .base import IVectorStore


class QdrantVectorStore(IVectorStore):
    """Qdrant client wrapper."""

    name = "qdrant"

    def __init__(self, url: str = "http://localhost:6333", api_key: Optional[str] = None) -> None:
        try:
            from qdrant_client import QdrantClient
        except ImportError as e:
            raise RuntimeError(
                "qdrant-client required. Install: pip install fast_vectors[qdrant]"
            ) from e
        self._client = QdrantClient(url=url, api_key=api_key)

    def upsert(
        self, index_name: str, vectors: List[tuple[str, List[float], Optional[dict[str, Any]]]]
    ) -> None:
        from qdrant_client.models import PointStruct

        points = [PointStruct(id=v[0], vector=v[1], payload=v[2] or {}) for v in vectors]
        self._client.upsert(collection_name=index_name, points=points)

    def query(
        self,
        index_name: str,
        vector: List[float],
        *,
        top_k: int = 10,
        filter: Optional[dict[str, Any]] = None,
    ) -> List[tuple[str, float, Optional[dict[str, Any]]]]:
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        q_filter = None
        if filter:
            q_filter = Filter(
                must=[FieldCondition(key=k, match=MatchValue(value=v)) for k, v in filter.items()]
            )
        r = self._client.search(
            collection_name=index_name, query_vector=vector, limit=top_k, query_filter=q_filter
        )
        return [(h.id, h.score or 0.0, h.payload) for h in r]

    def delete_index(self, index_name: str) -> None:
        self._client.delete_collection(index_name)
