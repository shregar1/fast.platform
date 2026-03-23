from typing import Any, List, Optional

import pytest

from data_platform.search.base import ISearchBackend
from tests.data_platform.search.abstraction import ISearchTests


class TestBackendsAbstract(ISearchTests):
    def test_isearch_backend_abstract_methods_raise_not_implemented(self) -> None:
        class DummyBackend(ISearchBackend):
            name = "dummy"

            def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
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
                return super().search(
                    index_name=index_name,
                    query=query,
                    limit=limit,
                    offset=offset,
                    filter=filter,
                    highlight_fields=highlight_fields,
                )

            def delete_index(self, index_name: str) -> None:
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
