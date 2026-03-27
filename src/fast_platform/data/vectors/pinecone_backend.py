"""Pinecone vector store backend."""

from __future__ import annotations

from typing import Any, List, Optional

from .base import IVectorStore


class PineconeVectorStore(IVectorStore):
    """Pinecone client wrapper."""

    name = "pinecone"

    def __init__(
        self,
        api_key: str,
        environment: Optional[str] = None,
        index_name: str = "fastmvc-index",
    ) -> None:
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
            environment: The environment parameter.
            index_name: The index_name parameter.
        """
        try:
            from pinecone import Pinecone
        except ImportError as e:
            raise RuntimeError(
                "pinecone-client required. Install: pip install fast_vectors[pinecone]"
            ) from e
        self._pc = Pinecone(api_key=api_key)
        self._index_name = index_name
        self._index = self._pc.Index(index_name)  # assumes index exists

    def upsert(
        self, index_name: str, vectors: List[tuple[str, List[float], Optional[dict[str, Any]]]]
    ) -> None:
        """Execute upsert operation.

        Args:
            index_name: The index_name parameter.
            vectors: The vectors parameter.

        Returns:
            The result of the operation.
        """
        idx = self._pc.Index(index_name) if index_name != self._index_name else self._index
        ids = [v[0] for v in vectors]
        values = [v[1] for v in vectors]
        metadata = [v[2] or {} for v in vectors]
        idx.upsert(vectors=list(zip(ids, values, metadata)))

    def query(
        self,
        index_name: str,
        vector: List[float],
        *,
        top_k: int = 10,
        filter: Optional[dict[str, Any]] = None,
    ) -> List[tuple[str, float, Optional[dict[str, Any]]]]:
        """Execute query operation.

        Args:
            index_name: The index_name parameter.
            vector: The vector parameter.
            top_k: The top_k parameter.
            filter: The filter parameter.

        Returns:
            The result of the operation.
        """
        idx = self._pc.Index(index_name) if index_name != self._index_name else self._index
        r = idx.query(vector=vector, top_k=top_k, filter=filter, include_metadata=True)
        return [(m.id, m.score or 0.0, m.metadata) for m in (r.matches or [])]

    def delete_index(self, index_name: str) -> None:
        """Execute delete_index operation.

        Args:
            index_name: The index_name parameter.

        Returns:
            The result of the operation.
        """
        self._pc.delete_index(index_name)
