"""OpenSearch backend."""

from __future__ import annotations

from typing import Any, List, Optional

from .base import ISearchBackend
from .dto import FacetedSearchResult, FacetBucket, SearchHit


class OpenSearchBackend(ISearchBackend):
    """OpenSearch client wrapper."""

    name = "opensearch"

    def __init__(
        self,
        hosts: List[str],
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        try:
            from opensearchpy import OpenSearch
        except ImportError as e:
            raise RuntimeError("opensearch-py required. Install: pip install fast_search[opensearch]") from e
        self._client = OpenSearch(
            hosts=hosts,
            http_auth=(username, password) if username and password else None,
            use_ssl="https" in (hosts or ["http://localhost"])[0],
            verify_certs=True,
        )

    def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
        for i, d in enumerate(documents):
            doc_id = d.get("id") or str(i)
            self._client.index(index=index_name, body=d, id=doc_id, refresh=True)

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
        _ = highlight_fields
        body: dict[str, Any] = {
            "query": {"simple_query_string": {"query": query}},
            "from": offset,
            "size": limit,
        }
        if filter:
            body["query"] = {"bool": {"must": [body["query"], {"term": filter}]}}
        r = self._client.search(index=index_name, body=body)
        return [h["_source"] for h in r.get("hits", {}).get("hits", [])]

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
        if not facet_fields and not highlight_fields:
            hits_raw = self.search(index_name, query, limit=limit, offset=offset, filter=filter)
            return FacetedSearchResult(
                hits=[SearchHit(document=d) for d in hits_raw],
                facets={},
                total=len(hits_raw),
            )

        body: dict[str, Any] = {
            "query": {"simple_query_string": {"query": query}},
            "from": offset,
            "size": limit,
        }
        if filter:
            body["query"] = {"bool": {"must": [body["query"], {"term": filter}]}}
        if highlight_fields:
            body["highlight"] = {"fields": {f: {} for f in highlight_fields}}
        if facet_fields:
            body["aggs"] = {f: {"terms": {"field": f, "size": 50}} for f in facet_fields}

        r = self._client.search(index=index_name, body=body)
        hits_raw = r.get("hits", {}).get("hits", [])
        total_raw = r.get("hits", {}).get("total", {})
        if isinstance(total_raw, dict):
            total_val = int(total_raw.get("value", len(hits_raw)))
        else:
            total_val = int(total_raw) if total_raw is not None else len(hits_raw)

        hits_out: list[SearchHit] = []
        for h in hits_raw:
            src = h.get("_source", {})
            hl: Optional[dict[str, List[str]]] = None
            if highlight_fields and "highlight" in h:
                hl = {k: list(v) if isinstance(v, list) else [str(v)] for k, v in h["highlight"].items()}
            hits_out.append(SearchHit(document=src, highlights=hl))

        facets: dict[str, list[FacetBucket]] = {}
        if facet_fields:
            aggs = r.get("aggregations") or {}
            for f in facet_fields:
                buckets = aggs.get(f, {}).get("buckets", [])
                facets[f] = [
                    FacetBucket(value=str(b.get("key")), count=int(b.get("doc_count", 0)))
                    for b in buckets
                ]

        return FacetedSearchResult(
            hits=hits_out,
            facets=facets,
            total=total_val,
        )

    def suggest(
        self,
        index_name: str,
        prefix: str,
        *,
        field: str = "title",
        limit: int = 10,
    ) -> List[str]:
        body: dict[str, Any] = {
            "query": {"match_phrase_prefix": {field: prefix}},
            "size": limit,
            "_source": [field],
        }
        r = self._client.search(index=index_name, body=body)
        out: List[str] = []
        seen: set[str] = set()
        for h in r.get("hits", {}).get("hits", []):
            src = h.get("_source", {})
            v = src.get(field)
            if isinstance(v, str) and v and v not in seen:
                seen.add(v)
                out.append(v)
        return out[:limit]

    def delete_index(self, index_name: str) -> None:
        self._client.indices.delete(index=index_name)
