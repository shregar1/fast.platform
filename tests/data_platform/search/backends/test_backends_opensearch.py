"""Module test_backends_opensearch.py."""

import types
from typing import Any

from tests.data_platform.search.abstraction import ISearchTests
from tests.data_platform.search.backends._install import install_module


class TestBackendsOpensearch(ISearchTests):
    """Represents the TestBackendsOpensearch class."""

    def test_opensearch_backend_index_search_delete_and_filter(self, monkeypatch) -> None:
        """Execute test_opensearch_backend_index_search_delete_and_filter operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        from fast_platform.data.search.opensearch_backend import OpenSearchBackend

        calls: dict[str, Any] = {}

        class FakeClient:
            """Represents the FakeClient class."""

            def __init__(self, **kwargs):
                """Execute __init__ operation."""
                calls["init_kwargs"] = kwargs

            def index(self, *, index: str, body: dict[str, Any], id: str, refresh: bool):
                """Execute index operation.

                Args:
                    index: The index parameter.
                    body: The body parameter.
                    id: The id parameter.
                    refresh: The refresh parameter.

                Returns:
                    The result of the operation.
                """
                calls.setdefault("index_calls", []).append(
                    {"index": index, "body": body, "id": id, "refresh": refresh}
                )

            def search(self, *, index: str, body: dict[str, Any]):
                """Execute search operation.

                Args:
                    index: The index parameter.
                    body: The body parameter.

                Returns:
                    The result of the operation.
                """
                calls["last_search_body"] = body
                q = body.get("query") or {}
                if "match_phrase_prefix" in q:
                    mp = q["match_phrase_prefix"]
                    field = next(iter(mp.keys()))
                    prefix = mp[field]
                    return {
                        "hits": {
                            "hits": [
                                {"_source": {field: f"{prefix} alpha"}},
                                {"_source": {field: f"{prefix} beta"}},
                            ],
                            "total": {"value": 2},
                        }
                    }
                hits_list: list[dict[str, Any]] = [{"_source": {"id": 1}}, {"_source": {"id": 2}}]
                if body.get("highlight") and hits_list:
                    fld = next(iter(body["highlight"]["fields"].keys()))
                    hits_list[0]["highlight"] = {fld: [f"<em>{fld}</em> hit"]}
                out: dict[str, Any] = {"hits": {"hits": hits_list, "total": {"value": 2}}}
                if "aggs" in body:
                    out["aggregations"] = {
                        f: {"buckets": [{"key": "x", "doc_count": 3}]} for f in body["aggs"].keys()
                    }
                return out

            class indices:
                """Represents the indices class."""

                @staticmethod
                def delete(*, index: str):
                    """Execute delete operation.

                    Args:
                        index: The index parameter.

                    Returns:
                        The result of the operation.
                    """
                    calls["deleted_index"] = index

        fake_mod = types.ModuleType("opensearchpy")
        fake_mod.OpenSearch = FakeClient
        install_module("opensearchpy", fake_mod)
        backend = OpenSearchBackend(hosts=["http://localhost:9200"], username="u", password="p")
        backend.index_documents("products", [{"name": "x"}, {"id": "doc-2", "name": "y"}])
        hits = backend.search("products", "query", limit=3, offset=2, filter={"category": "books"})
        assert hits == [{"id": 1}, {"id": 2}]
        assert "bool" in calls["last_search_body"]["query"]
        assert calls["last_search_body"]["from"] == 2
        assert calls["last_search_body"]["size"] == 3
        fr = backend.search_faceted(
            "products",
            "query",
            limit=3,
            offset=2,
            filter={"category": "books"},
            facet_fields=["category"],
        )
        assert fr.total == 2
        assert "category" in fr.facets
        fr_hl = backend.search_faceted(
            "products", "query", limit=3, offset=0, highlight_fields=["title"]
        )
        assert fr_hl.hits[0].highlights is not None
        assert "title" in fr_hl.hits[0].highlights
        assert backend.suggest("products", "wid", field="title", limit=5) == [
            "wid alpha",
            "wid beta",
        ]
        backend.delete_index("products")
        assert calls["deleted_index"] == "products"
