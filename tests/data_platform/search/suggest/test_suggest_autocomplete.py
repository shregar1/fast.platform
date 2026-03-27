"""Module test_suggest_autocomplete.py."""

from __future__ import annotations

"""Tests for :func:`data.search.suggest.suggest_autocomplete`."""
from typing import Any, List, Optional

from fast_platform.data.search.base import ISearchBackend
from fast_platform.data.search.suggest import suggest_autocomplete
from tests.data_platform.search.abstraction import ISearchTests


class StubSuggestBackend(ISearchBackend):
    """Represents the StubSuggestBackend class."""

    name = "stub"

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self.suggest_calls: list[dict[str, Any]] = []

    def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
        """Execute index_documents operation.

        Args:
            index_name: The index_name parameter.
            documents: The documents parameter.

        Returns:
            The result of the operation.
        """
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
        raise NotImplementedError

    def delete_index(self, index_name: str) -> None:
        """Execute delete_index operation.

        Args:
            index_name: The index_name parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError

    def suggest(
        self, index_name: str, prefix: str, *, field: str = "title", limit: int = 10
    ) -> List[str]:
        """Execute suggest operation.

        Args:
            index_name: The index_name parameter.
            prefix: The prefix parameter.
            field: The field parameter.
            limit: The limit parameter.

        Returns:
            The result of the operation.
        """
        self.suggest_calls.append(
            {"index_name": index_name, "prefix": prefix, "field": field, "limit": limit}
        )
        return ["one", "two"]


class TestSuggestAutocomplete(ISearchTests):
    """Represents the TestSuggestAutocomplete class."""

    def test_suggest_autocomplete_delegates_to_backend(self) -> None:
        """Execute test_suggest_autocomplete_delegates_to_backend operation.

        Returns:
            The result of the operation.
        """
        b = StubSuggestBackend()
        out = suggest_autocomplete(b, "idx", "pre", field="name", limit=5)
        assert out == ["one", "two"]
        assert b.suggest_calls == [
            {"index_name": "idx", "prefix": "pre", "field": "name", "limit": 5}
        ]
