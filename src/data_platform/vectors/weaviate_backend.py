"""Weaviate vector store backend."""

from __future__ import annotations

from typing import Any, List, Optional

from .base import IVectorStore


class WeaviateVectorStore(IVectorStore):
    """Weaviate client wrapper."""

    name = "weaviate"

    def __init__(self, url: str = "http://localhost:8080", api_key: Optional[str] = None) -> None:
        try:
            import weaviate
        except ImportError as e:
            raise RuntimeError(
                "weaviate-client required. Install: pip install fast_vectors[weaviate]"
            ) from e
        from urllib.parse import urlparse

        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if parsed.scheme == "https" else 8080)
        if api_key:
            self._client = weaviate.connect_to_weaviate_cloud(
                cluster_url=url.replace("https://", "").replace("http://", "").split(":")[0],
                auth_credentials=weaviate.auth.AuthApiKey(api_key),
            )
        else:
            self._client = weaviate.connect_to_local(host=host, port=port, grpc_port=50051)

    def upsert(
        self, index_name: str, vectors: List[tuple[str, List[float], Optional[dict[str, Any]]]]
    ) -> None:
        with self._client.collections.get(index_name).batch.dynamic() as batch:
            for vid, vec, meta in vectors:
                batch.add_object(properties=meta or {}, vector=vec)

    def query(
        self,
        index_name: str,
        vector: List[float],
        *,
        top_k: int = 10,
        filter: Optional[dict[str, Any]] = None,
    ) -> List[tuple[str, float, Optional[dict[str, Any]]]]:
        coll = self._client.collections.get(index_name)
        r = coll.query.near_vector(near_vector=vector, limit=top_k)
        return [(str(o.uuid), o.metadata.distance or 0.0, dict(o.properties)) for o in r.objects]

    def delete_index(self, index_name: str) -> None:
        self._client.collections.delete(index_name)
