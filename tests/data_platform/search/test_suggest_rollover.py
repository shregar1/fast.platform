from __future__ import annotations
"""Tests for suggest_autocomplete and swap_index_alias."""
from tests.data_platform.search.abstraction import ISearchTests

from typing import Any, List, Optional
from search.base import ISearchBackend
from search.rollover import swap_index_alias
from search.suggest import suggest_autocomplete

class _StubBackend(ISearchBackend):
    name = 'stub'

    def __init__(self) -> None:
        self.suggest_calls: list[dict[str, Any]] = []

    def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
        raise NotImplementedError

    def search(self, index_name: str, query: str, *, limit: int=20, offset: int=0, filter: Optional[dict[str, Any]]=None, highlight_fields: Optional[List[str]]=None) -> List[dict[str, Any]]:
        raise NotImplementedError

    def delete_index(self, index_name: str) -> None:
        raise NotImplementedError

    def suggest(self, index_name: str, prefix: str, *, field: str='title', limit: int=10) -> List[str]:
        self.suggest_calls.append({'index_name': index_name, 'prefix': prefix, 'field': field, 'limit': limit})
        return ['one', 'two']

class TestSuggestRollover(ISearchTests):

    def test_suggest_autocomplete_delegates_to_backend(self):
        b = _StubBackend()
        out = suggest_autocomplete(b, 'idx', 'pre', field='name', limit=5)
        assert out == ['one', 'two']
        assert b.suggest_calls == [{'index_name': 'idx', 'prefix': 'pre', 'field': 'name', 'limit': 5}]

    def test_swap_index_alias_remove_and_add(self):

        class _Indices:

            def __init__(self) -> None:
                self.last_body: Optional[dict[str, Any]] = None

            def update_aliases(self, body: dict[str, Any]) -> None:
                self.last_body = body

        class _Client:

            def __init__(self) -> None:
                self.indices = _Indices()
        c = _Client()
        swap_index_alias(c, alias='products', add_index='products_v2', remove_index='products_v1')
        assert c.indices.last_body == {'actions': [{'remove': {'index': 'products_v1', 'alias': 'products'}}, {'add': {'index': 'products_v2', 'alias': 'products'}}]}

    def test_swap_index_alias_add_only(self):

        class _Indices:

            def __init__(self) -> None:
                self.last_body: Optional[dict[str, Any]] = None

            def update_aliases(self, body: dict[str, Any]) -> None:
                self.last_body = body

        class _Client:

            def __init__(self) -> None:
                self.indices = _Indices()
        c = _Client()
        swap_index_alias(c, alias='products', add_index='products_v1')
        assert c.indices.last_body == {'actions': [{'add': {'index': 'products_v1', 'alias': 'products'}}]}
