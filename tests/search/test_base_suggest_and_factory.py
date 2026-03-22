"""ISearchBackend.suggest default impl and build_search_backend branches."""

from __future__ import annotations

import sys
import types
from typing import Any, List, Optional

import pytest

from fast_search.base import ISearchBackend, build_search_backend


def _install_fake_typesense() -> None:
    m = types.ModuleType("typesense")

    class Client:
        def __init__(self, _cfg: object) -> None:
            pass

    m.Client = Client  # type: ignore[attr-defined]
    sys.modules["typesense"] = m


def _install_fake_meilisearch() -> None:
    m = types.ModuleType("meilisearch")

    class Client:
        def __init__(self, _url: str, _key: object = None) -> None:
            pass

    m.Client = Client  # type: ignore[attr-defined]
    sys.modules["meilisearch"] = m


def _install_fake_opensearch() -> None:
    m = types.ModuleType("opensearchpy")

    class OpenSearch:
        def __init__(self, **_kwargs: object) -> None:
            pass

    m.OpenSearch = OpenSearch  # type: ignore[attr-defined]
    sys.modules["opensearchpy"] = m


def _cleanup(*names: str) -> None:
    for n in names:
        sys.modules.pop(n, None)


class _ListBackend(ISearchBackend):
    name = "stub"

    def __init__(self, hits: List[dict[str, Any]]) -> None:
        self._hits = hits

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
        _ = highlight_fields
        return self._hits[:limit]

    def delete_index(self, index_name: str) -> None:
        raise NotImplementedError


def test_suggest_dedupe_prefix_filter_and_limit() -> None:
    b = _ListBackend(
        [
            {"title": "alpha widget"},
            {"title": "beta"},
            {"title": "  "},
            {"n": 1},
            {"title": "alpha duplicate"},
        ]
    )
    out = b.suggest("i", "alp", field="title", limit=2)
    assert "alpha widget" in out
    assert len(out) <= 2


def test_suggest_empty_prefix_accepts_values() -> None:
    b = _ListBackend([{"title": "z"}])
    assert b.suggest("i", "", field="title", limit=5) == ["z"]


def test_search_faceted_default_wraps_search() -> None:
    b = _ListBackend([{"a": 1}])
    fr = b.search_faceted("i", "q", highlight_fields=None)
    assert fr.total == 1
    assert fr.hits[0].document == {"a": 1}


def test_build_search_backend_typesense_and_opensearch(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_typesense()
    _install_fake_opensearch()
    try:
        class Cfg:
            meilisearch = type("M", (), {"enabled": False, "url": None})()
            typesense = type("T", (), {"enabled": True, "host": "h", "port": 80, "protocol": "http", "api_key": "k"})()
            opensearch = type("O", (), {"enabled": True, "hosts": ["http://os"], "username": None, "password": None})()

        class SearchConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("fast_search.base.SearchConfiguration", SearchConfiguration)
        ts = build_search_backend("typesense")
        assert ts is not None
        osb = build_search_backend("opensearch")
        assert osb is not None
    finally:
        _cleanup("typesense", "opensearchpy")


def test_build_search_backend_meilisearch_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_meilisearch()
    try:
        class Cfg:
            meilisearch = type("M", (), {"enabled": True, "url": "http://m", "api_key": "k"})()
            typesense = type("T", (), {"enabled": False})()
            opensearch = type("O", (), {"enabled": False, "hosts": []})()

        class SearchConfiguration:
            def get_config(self):
                return Cfg()

        monkeypatch.setattr("fast_search.base.SearchConfiguration", SearchConfiguration)
        m = build_search_backend("meilisearch")
        assert m is not None
    finally:
        _cleanup("meilisearch")
