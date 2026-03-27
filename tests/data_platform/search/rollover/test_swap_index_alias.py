"""Module test_swap_index_alias.py."""

from __future__ import annotations

"""Tests for :func:`data.search.rollover.swap_index_alias`."""
from typing import Any, Optional

from fast_platform.data.search.rollover import swap_index_alias
from tests.data_platform.search.abstraction import ISearchTests


class TestSwapIndexAlias(ISearchTests):
    """Represents the TestSwapIndexAlias class."""

    def test_swap_index_alias_remove_and_add(self) -> None:
        """Execute test_swap_index_alias_remove_and_add operation.

        Returns:
            The result of the operation.
        """

        class _Indices:
            """Represents the _Indices class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.last_body: Optional[dict[str, Any]] = None

            def update_aliases(self, body: dict[str, Any]) -> None:
                """Execute update_aliases operation.

                Args:
                    body: The body parameter.

                Returns:
                    The result of the operation.
                """
                self.last_body = body

        class _Client:
            """Represents the _Client class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
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
        """Execute test_swap_index_alias_add_only operation.

        Returns:
            The result of the operation.
        """

        class _Indices:
            """Represents the _Indices class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.last_body: Optional[dict[str, Any]] = None

            def update_aliases(self, body: dict[str, Any]) -> None:
                """Execute update_aliases operation.

                Args:
                    body: The body parameter.

                Returns:
                    The result of the operation.
                """
                self.last_body = body

        class _Client:
            """Represents the _Client class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.indices = _Indices()

        c = _Client()
        swap_index_alias(c, alias="products", add_index="products_v1")
        assert c.indices.last_body == {
            "actions": [{"add": {"index": "products_v1", "alias": "products"}}]
        }
