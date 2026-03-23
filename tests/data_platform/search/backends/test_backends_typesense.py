import types
from typing import Any

from tests.data_platform.search.abstraction import ISearchTests
from tests.data_platform.search.backends._install import install_module


class TestBackendsTypesense(ISearchTests):
    def test_typesense_backend_index_search_delete_and_filter(self, monkeypatch) -> None:
        from data_platform.search.typesense_backend import TypesenseBackend, _filter_str

        calls: dict[str, Any] = {}

        class FakeDocuments:
            def upsert(self, d: dict[str, Any]):
                calls.setdefault("upserts", []).append(d)

            def search(self, body: dict[str, Any]):
                calls["last_search_body"] = body
                hits: list[dict[str, Any]] = [{"document": {"id": "a"}}, {"document": {"id": "b"}}]
                if body.get("highlight_fields"):
                    hits[0]["highlight"] = {"title": ["<em>widget</em>"]}
                out: dict[str, Any] = {"hits": hits, "found": 2}
                if body.get("facet_by"):
                    out["facet_counts"] = [
                        {"field_name": "k", "counts": [{"count": 2, "value": "v"}]},
                        {"counts": []},
                        {"fieldName": "alt", "counts": [{"count": 1, "value": "z"}]},
                    ]
                return out

        class FakeCollection:
            def __init__(self):
                self.documents = FakeDocuments()

            def delete(self):
                calls["deleted_collection"] = True

        class FakeCollections:
            def __init__(self):
                self._cols: dict[str, FakeCollection] = {}

            def __getitem__(self, name: str) -> FakeCollection:
                if name not in self._cols:
                    self._cols[name] = FakeCollection()
                return self._cols[name]

        class FakeTypesenseClient:
            def __init__(self, cfg):
                calls["client_cfg"] = cfg
                self.collections = FakeCollections()

        fake_mod = types.ModuleType("typesense")
        fake_mod.Client = FakeTypesenseClient
        install_module("typesense", fake_mod)
        backend = TypesenseBackend(host="localhost", port=8108, protocol="http", api_key=None)
        backend.index_documents("products", [{"name": "x"}, {"name": "y"}])
        hits = backend.search("products", "widget", limit=10, offset=20, filter={"k": "v"})
        assert hits == [{"id": "a"}, {"id": "b"}]
        assert _filter_str({"k": "v"}) == "k:v"
        assert calls["last_search_body"]["filter_by"] == "k:v"
        fr = backend.search_faceted(
            "products", "widget", limit=10, offset=20, filter={"k": "v"}, facet_fields=["k"]
        )
        assert fr.total == 2
        assert "k" in fr.facets
        fr_hl = backend.search_faceted(
            "products", "widget", limit=10, offset=20, highlight_fields=["title"]
        )
        assert fr_hl.hits[0].highlights is not None
        assert "title" in fr_hl.hits[0].highlights
        backend.delete_index("products")
        assert calls.get("deleted_collection") is True
