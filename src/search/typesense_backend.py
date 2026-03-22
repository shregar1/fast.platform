"""Typesense backend."""

from __future__ import annotations

from typing import Any, List, Optional

from .base import ISearchBackend
from .dto import FacetedSearchResult, FacetBucket, SearchHit


class TypesenseBackend(ISearchBackend):
    """Typesense client wrapper."""

    name = "typesense"

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8108,
        protocol: str = "http",
        api_key: Optional[str] = None,
    ):
        try:
            from typesense import Client
        except ImportError as e:
            raise RuntimeError("typesense required. Install: pip install fast_search[typesense]") from e
        self._client = Client({
            "nodes": [{"host": host, "port": str(port), "protocol": protocol}],
            "api_key": api_key or "xyz",
            "connection_timeout_seconds": 2,
        })

    def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
        for d in documents:
            self._client.collections[index_name].documents.upsert(d)

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
        r = self._client.collections[index_name].documents.search({
            "q": query,
            "per_page": limit,
            "page": (offset // limit) + 1 if limit else 1,
            "filter_by": _filter_str(filter) if filter else None,
        })
        return [h["document"] for h in r.get("hits", [])]

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
        body: dict[str, Any] = {
            "q": query,
            "per_page": limit,
            "page": (offset // limit) + 1 if limit else 1,
            "filter_by": _filter_str(filter) if filter else None,
        }
        if facet_fields:
            body["facet_by"] = ",".join(facet_fields)
        if highlight_fields:
            body["highlight_fields"] = ",".join(highlight_fields)
        r = self._client.collections[index_name].documents.search(body)
        hits_raw = r.get("hits", [])
        facets: dict[str, list[FacetBucket]] = {}
        for fc in r.get("facet_counts", []) or []:
            fn = fc.get("field_name") or fc.get("fieldName")
            if not fn:
                continue
            facets[fn] = [
                FacetBucket(value=str(c.get("value", "")), count=int(c.get("count", 0)))
                for c in (fc.get("counts") or [])
            ]
        found = len(hits_raw)
        if isinstance(r.get("found"), int):
            found = int(r["found"])

        hits_out: list[SearchHit] = []
        for h in hits_raw:
            doc = h.get("document", {})
            hl: Optional[dict[str, List[str]]] = None
            if highlight_fields and "highlight" in h:
                raw_hl = h["highlight"]
                if isinstance(raw_hl, dict):
                    hl = {k: list(v) if isinstance(v, list) else [str(v)] for k, v in raw_hl.items()}
            hits_out.append(SearchHit(document=doc, highlights=hl))

        return FacetedSearchResult(
            hits=hits_out,
            facets=facets,
            total=found,
        )

    def delete_index(self, index_name: str) -> None:
        self._client.collections[index_name].delete()


def _filter_str(f: dict[str, Any]) -> str:
    return " && ".join(f"{k}:{v}" for k, v in f.items())
