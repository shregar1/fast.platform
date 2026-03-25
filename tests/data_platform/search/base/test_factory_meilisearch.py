from __future__ import annotations

"""Tests for :func:`data.search.base.build_search_backend` (meilisearch)."""
import pytest

from data.search.base import build_search_backend
from tests.data_platform.search._fake_search_modules import (
    cleanup_fake_modules,
    install_fake_meilisearch,
)
from tests.data_platform.search.abstraction import ISearchTests


class TestSearchFactoryMeilisearch(ISearchTests):
    def test_build_search_backend_meilisearch_when_enabled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        install_fake_meilisearch()
        try:

            class Cfg:
                meilisearch = type("M", (), {"enabled": True, "url": "http://m", "api_key": "k"})()
                typesense = type("T", (), {"enabled": False})()
                opensearch = type("O", (), {"enabled": False, "hosts": []})()

            class SearchConfiguration:
                def get_config(self):
                    return Cfg()

            monkeypatch.setattr("data.search.base.SearchConfiguration", SearchConfiguration)
            m = build_search_backend("meilisearch")
            assert m is not None
        finally:
            cleanup_fake_modules("meilisearch")
