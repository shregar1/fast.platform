import types
from typing import Any, List, Optional

from tests.data_platform.search.abstraction import ISearchTests
from tests.data_platform.search.backends._install import install_module


class TestBackendsMeilisearch(ISearchTests):
    def test_build_search_backend_meilisearch_and_methods(self, monkeypatch) -> None:
        from search import base as search_base

        class FakeIndex:
            def __init__(self):
                self.added: list[tuple[str, list[dict[str, Any]]]] = []
                self.last_search: dict[str, Any] = {}

            def add_documents(self, documents: List[dict[str, Any]]):
                self.added.append(("default", documents))

            def search(self, query: str, **kwargs: Any):
                self.last_search = {"query": query, **kwargs}
                hits: list[dict[str, Any]] = [{"id": 1}, {"id": 2}]
                if kwargs.get("attributesToHighlight"):
                    hits[0]["_formatted"] = {"title": "<em>w</em>idget"}
                out: dict[str, Any] = {"hits": hits, "estimatedTotalHits": 2}
                if kwargs.get("facets"):
                    out["facetDistribution"] = {"genre": {"a": 1, "b": 1}}
                return out

        class FakeMeiliClient:
            def __init__(self, url: str, api_key: Optional[str] = None):
                self.url = url
                self.api_key = api_key
                self._index = FakeIndex()

            def index(self, index_name: str) -> FakeIndex:
                return self._index

            def delete_index(self, index_name: str) -> None:
                self.deleted = index_name

        fake_mod = types.ModuleType("meilisearch")
        fake_mod.Client = FakeMeiliClient
        install_module("meilisearch", fake_mod)

        class FakeCfg:
            def __init__(self):
                self.meilisearch = types.SimpleNamespace(
                    enabled=True, url="http://localhost:7700", api_key="k"
                )
                self.typesense = types.SimpleNamespace(enabled=False)
                self.opensearch = types.SimpleNamespace(enabled=False)

        monkeypatch.setattr(
            search_base,
            "SearchConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        backend = search_base.build_search_backend("meilisearch")
        assert backend is not None
        docs = [{"a": 1}]
        backend.index_documents("products", docs)
        hits = backend.search("products", "widget", limit=10, offset=5, filter={"type": "x"})
        assert hits == [{"id": 1}, {"id": 2}]
        fr = backend.search_faceted(
            "products", "widget", limit=10, offset=5, facet_fields=["genre"]
        )
        assert len(fr.hits) == 2
        assert fr.total == 2
        assert "genre" in fr.facets
        assert len(fr.facets["genre"]) == 2
        fr_hl = backend.search_faceted(
            "products", "widget", limit=10, offset=5, highlight_fields=["title"]
        )
        assert fr_hl.hits[0].highlights is not None
        assert "title" in fr_hl.hits[0].highlights
        backend.delete_index("products")
