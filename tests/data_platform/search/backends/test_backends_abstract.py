"""Module test_backends_abstract.py."""

from typing import Any, List, Optional

import pytest

from data.search.base import ISearchBackend
from tests.data_platform.search.abstraction import ISearchTests


class TestBackendsAbstract(ISearchTests):
    """Represents the TestBackendsAbstract class."""

    def test_isearch_backend_abstract_methods_raise_not_implemented(self) -> None:
        """Execute test_isearch_backend_abstract_methods_raise_not_implemented operation.

        Returns:
            The result of the operation.
        """

        class DummyBackend(ISearchBackend):
            """Represents the DummyBackend class."""

            name = "dummy"

            def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
                """Execute index_documents operation.

                Args:
                    index_name: The index_name parameter.
                    documents: The documents parameter.

                Returns:
                    The result of the operation.
                """
                return super().index_documents(index_name=index_name, documents=documents)

            def search(
                self,
                index_name: str,
                query: str,
                *,
                limit: int = 20,
                offset: int = 0,
                filter: Optional[dict[str, Any]] = None,
                highlight_fields: Optional[List[str]] = None,
            ):
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
                return super().search(
                    index_name=index_name,
                    query=query,
                    limit=limit,
                    offset=offset,
                    filter=filter,
                    highlight_fields=highlight_fields,
                )

            def delete_index(self, index_name: str) -> None:
                """Execute delete_index operation.

                Args:
                    index_name: The index_name parameter.

                Returns:
                    The result of the operation.
                """
                return super().delete_index(index_name=index_name)

        b = DummyBackend()
        with pytest.raises(NotImplementedError):
            b.index_documents("i", [{"a": 1}])
        with pytest.raises(NotImplementedError):
            b.search("i", "q")
        with pytest.raises(NotImplementedError):
            b.delete_index("i")
        with pytest.raises(NotImplementedError):
            b.search_faceted("i", "q")
