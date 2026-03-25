from __future__ import annotations

"""Tests for :func:`data.search.rollover.swap_index_alias`."""
from typing import Any, Optional

from data.search.rollover import swap_index_alias
from tests.data_platform.search.abstraction import ISearchTests


class TestSwapIndexAlias(ISearchTests):
    def test_swap_index_alias_remove_and_add(self) -> None:
        class _Indices:
            def __init__(self) -> None:
                self.last_body: Optional[dict[str, Any]] = None

            def update_aliases(self, body: dict[str, Any]) -> None:
                self.last_body = body

        class _Client:
            def __init__(self) -> None:
                self.indices = _Indices()

        c = _Client()
        swap_index_alias(c, alias="products", add_index="products_v2", remove_index="products_v1")
        assert c.indices.last_body == {
            "actions": [
                {"remove": {"index": "products_v1", "alias": "products"}},
                {"add": {"index": "products_v2", "alias": "products"}},
            ]
        }

    def test_swap_index_alias_add_only(self) -> None:
        class _Indices:
            def __init__(self) -> None:
                self.last_body: Optional[dict[str, Any]] = None

            def update_aliases(self, body: dict[str, Any]) -> None:
                self.last_body = body

        class _Client:
            def __init__(self) -> None:
                self.indices = _Indices()

        c = _Client()
        swap_index_alias(c, alias="products", add_index="products_v1")
        assert c.indices.last_body == {
            "actions": [{"add": {"index": "products_v1", "alias": "products"}}]
        }
