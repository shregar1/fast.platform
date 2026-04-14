"""Meilisearch backend."""

from __future__ import annotations

from .constants import MEILISEARCH_BACKEND
from typing import Any, List, Optional

from .base import ISearchBackend
from ...core.dtos.search import FacetBucket, FacetedSearchResult, SearchHit


def _strip_meili_meta(hit: dict[str, Any]) -> dict[str, Any]:
    """Execute _strip_meili_meta operation.

    Args:
        hit: The hit parameter.

    Returns:
        The result of the operation.
    """
    return {k: v for k, v in hit.items() if k not in ("_formatted", "_matchesPosition")}


def _meili_highlights(hit: dict[str, Any]) -> Optional[dict[str, List[str]]]:
    """Execute _meili_highlights operation.

    Args:
        hit: The hit parameter.

    Returns:
        The result of the operation.
    """
    fmt = hit.get("_formatted")
    if not isinstance(fmt, dict):
        return None
    out: dict[str, List[str]] = {}
    for k, v in fmt.items():
        if isinstance(v, str):
            out[k] = [v]
    return out or None


class MeilisearchBackend(ISearchBackend):
    """Meilisearch client wrapper."""

    name = MEILISEARCH_BACKEND

    def __init__(self, url: str, api_key: Optional[str] = None) -> None:
        """Execute __init__ operation.

        Args:
            url: The url parameter.
            api_key: The api_key parameter.
        """
        try:
            from meilisearch import Client
        except ImportError as e:
            raise RuntimeError(
                "meilisearch required. Install: pip install fast_search[meilisearch]"
            ) from e
        self._client = Client(url, api_key)

    def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
        """Execute index_documents operation.

        Args:
            index_name: The index_name parameter.
            documents: The documents parameter.

        Returns:
            The result of the operation.
        """
        index = self._client.index(index_name)
        index.add_documents(documents)

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
        """Execute search operation.

        Args:
            index_name: The index_name parameter.
            query: The query parameter.
            limit: The limit parameter.
            offset: The offset parameter.
            filter: The filter parameter.
            highlight_fields: The highlight_fields parameter.

        Returns:
            The result of the operation.
        """
        index = self._client.index(index_name)
        kwargs: dict[str, Any] = {"limit": limit, "offset": offset}
        if filter is not None:
            kwargs["filter"] = filter
        if highlight_fields:
            kwargs["attributesToHighlight"] = highlight_fields
        r = index.search(query, **kwargs)
        raw_hits = r.get("hits", [])
        return [_strip_meili_meta(h) for h in raw_hits]

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
        """Execute search_faceted operation.

        Args:
            index_name: The index_name parameter.
            query: The query parameter.
            limit: The limit parameter.
            offset: The offset parameter.
            filter: The filter parameter.
            facet_fields: The facet_fields parameter.
            highlight_fields: The highlight_fields parameter.

        Returns:
            The result of the operation.
        """
        index = self._client.index(index_name)
        kwargs: dict[str, Any] = {"limit": limit, "offset": offset}
        if filter is not None:
            kwargs["filter"] = filter
        if facet_fields:
            kwargs["facets"] = facet_fields
        if highlight_fields:
            kwargs["attributesToHighlight"] = highlight_fields
        r = index.search(query, **kwargs)
        hits_raw = r.get("hits", [])
        total = r.get("estimatedTotalHits")
        if total is None:
            total = r.get("nbHits")
        if total is None:
            total = len(hits_raw)
        facets: dict[str, list[FacetBucket]] = {}
        for field, dist in (r.get("facetDistribution") or {}).items():
            facets[field] = [FacetBucket(value=str(k), count=int(v)) for k, v in dist.items()]
        hits_out: list[SearchHit] = []
        for h in hits_raw:
            doc = _strip_meili_meta(h)
            hl = _meili_highlights(h) if highlight_fields else None
            hits_out.append(SearchHit(document=doc, highlights=hl))
        return FacetedSearchResult(
            hits=hits_out,
            facets=facets,
            total=int(total),
        )

    def delete_index(self, index_name: str) -> None:
        """Execute delete_index operation.

        Args:
            index_name: The index_name parameter.

        Returns:
            The result of the operation.
        """
        self._client.delete_index(index_name)
