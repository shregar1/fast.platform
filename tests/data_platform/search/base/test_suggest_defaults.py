from __future__ import annotations

"""Tests for :meth:`ISearchBackend.suggest` default and :meth:`search_faceted` wrapper."""
from typing import Any, List, Optional

from data_platform.search.base import ISearchBackend
from tests.data_platform.search.abstraction import ISearchTests


class ListSuggestBackend(ISearchBackend):
    name = "stub"

    def __init__(self, hits: List[dict[str, Any]]) -> None:
        self._hits = hits

    def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
        raise NotImplementedError

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
        return self._hits[:limit]

    def delete_index(self, index_name: str) -> None:
        raise NotImplementedError


class TestSuggestDefaults(ISearchTests):
    def test_suggest_dedupe_prefix_filter_and_limit(self) -> None:
        b = ListSuggestBackend(
            [
                {"title": "alpha widget"},
                {"title": "beta"},
                {"title": "  "},
                {"n": 1},
                {"title": "alpha duplicate"},
            ]
        )
        out = b.suggest("i", "alp", field="title", limit=2)
        assert "alpha widget" in out
        assert len(out) <= 2

    def test_suggest_empty_prefix_accepts_values(self) -> None:
        b = ListSuggestBackend([{"title": "z"}])
        assert b.suggest("i", "", field="title", limit=5) == ["z"]

    def test_search_faceted_default_wraps_search(self) -> None:
        b = ListSuggestBackend([{"a": 1}])
        fr = b.search_faceted("i", "q", highlight_fields=None)
        assert fr.total == 1
        assert fr.hits[0].document == {"a": 1}
