from __future__ import annotations

"""Tests for :func:`data.search.suggest.suggest_autocomplete`."""
from typing import Any, List, Optional

from data.search.base import ISearchBackend
from data.search.suggest import suggest_autocomplete
from tests.data_platform.search.abstraction import ISearchTests


class StubSuggestBackend(ISearchBackend):
    name = "stub"

    def __init__(self) -> None:
        self.suggest_calls: list[dict[str, Any]] = []

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
        raise NotImplementedError

    def delete_index(self, index_name: str) -> None:
        raise NotImplementedError

    def suggest(
        self, index_name: str, prefix: str, *, field: str = "title", limit: int = 10
    ) -> List[str]:
        self.suggest_calls.append(
            {"index_name": index_name, "prefix": prefix, "field": field, "limit": limit}
        )
        return ["one", "two"]


class TestSuggestAutocomplete(ISearchTests):
    def test_suggest_autocomplete_delegates_to_backend(self) -> None:
        b = StubSuggestBackend()
        out = suggest_autocomplete(b, "idx", "pre", field="name", limit=5)
        assert out == ["one", "two"]
        assert b.suggest_calls == [
            {"index_name": "idx", "prefix": "pre", "field": "name", "limit": 5}
        ]
