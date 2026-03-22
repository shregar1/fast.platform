"""
Search backend interface and factory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional

from from fast_platform import SearchConfiguration

from .dto import FacetedSearchResult, SearchHit


class ISearchBackend(ABC):
    """Interface for search backends (Meilisearch, Typesense, OpenSearch)."""

    name: str

    @abstractmethod
    def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
        """Index or upsert documents."""
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        index_name: str,
        query: str,
        *,
        limit: int = 20,
        offset: int = 0,
        filter: Optional[dict[str, Any]] = None,
        highlight_fields: Optional[List[str]] = None,
    ) -> List[dict[str, Any]]:
        """Search and return list of hits (document payloads)."""
        raise NotImplementedError

    def suggest(
        self,
        index_name: str,
        prefix: str,
        *,
        field: str = "title",
        limit: int = 10,
    ) -> List[str]:
        """
        Autocomplete-style suggestions as distinct string values from ``field``.

        Default uses :meth:`search` with the prefix as query and dedupes by field value;
        backends may override for native completion / prefix APIs.
        """
        hits = self.search(index_name, prefix, limit=max(limit * 3, limit), offset=0)
        out: List[str] = []
        seen: set[str] = set()
        pl = prefix.lower()
        for h in hits:
            v = h.get(field)
            if not isinstance(v, str) or not v.strip():
                continue
            if pl and pl not in v.lower():
                continue
            if v not in seen:
                seen.add(v)
                out.append(v)
            if len(out) >= limit:
                break
        return out

    def search_faceted(
        self,
        index_name: str,
        query: str,
        *,
        limit: int = 20,
        offset: int = 0,
        filter: Optional[dict[str, Any]] = None,
        facet_fields: Optional[List[str]] = None,
        highlight_fields: Optional[List[str]] = None,
    ) -> FacetedSearchResult:
        """
        Search with optional facet fields. Default implementation wraps :meth:`search`
        and returns empty ``facets``; backends may override for native facet support.

        When ``highlight_fields`` is set, backends that support it fill :attr:`SearchHit.highlights`.
        """
        _ = facet_fields
        hits_raw = self.search(
            index_name,
            query,
            limit=limit,
            offset=offset,
            filter=filter,
            highlight_fields=highlight_fields,
        )
        return FacetedSearchResult(
            hits=[SearchHit(document=d) for d in hits_raw],
            facets={},
            total=len(hits_raw),
        )

    @abstractmethod
    def delete_index(self, index_name: str) -> None:
        """Delete an index."""
        raise NotImplementedError


def build_search_backend(backend: str = "meilisearch") -> Optional[ISearchBackend]:
    """
    Build a search backend from SearchConfiguration (config/search/config.json).
    backend: "meilisearch" | "typesense" | "opensearch"
    """
    cfg = SearchConfiguration().get_config()

    if backend == "meilisearch" and getattr(cfg.meilisearch, "enabled", False) and cfg.meilisearch.url:
        try:
            from .meilisearch_backend import MeilisearchBackend
            return MeilisearchBackend(
                url=cfg.meilisearch.url,
                api_key=cfg.meilisearch.api_key,
            )
        except ImportError:
            return None

    if backend == "typesense" and getattr(cfg.typesense, "enabled", False):
        try:
            from .typesense_backend import TypesenseBackend
            return TypesenseBackend(
                host=cfg.typesense.host,
                port=cfg.typesense.port,
                protocol=cfg.typesense.protocol,
                api_key=cfg.typesense.api_key,
            )
        except ImportError:
            return None

    if backend == "opensearch" and getattr(cfg.opensearch, "enabled", False) and cfg.opensearch.hosts:
        try:
            from .opensearch_backend import OpenSearchBackend
            return OpenSearchBackend(
                hosts=cfg.opensearch.hosts,
                username=cfg.opensearch.username,
                password=cfg.opensearch.password,
            )
        except ImportError:
            return None

    return None
