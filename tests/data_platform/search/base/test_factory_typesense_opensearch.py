from __future__ import annotations

"""Tests for :func:`data.search.base.build_search_backend` (typesense + opensearch)."""
import pytest

from data.search.base import build_search_backend
from tests.data_platform.search._fake_search_modules import (
    cleanup_fake_modules,
    install_fake_opensearch,
    install_fake_typesense,
)
from tests.data_platform.search.abstraction import ISearchTests


class TestSearchFactoryTypesenseOpensearch(ISearchTests):
    def test_build_search_backend_typesense_and_opensearch(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        install_fake_typesense()
        install_fake_opensearch()
        try:

            class Cfg:
                meilisearch = type("M", (), {"enabled": False, "url": None})()
                typesense = type(
                    "T",
                    (),
                    {"enabled": True, "host": "h", "port": 80, "protocol": "http", "api_key": "k"},
                )()
                opensearch = type(
                    "O",
                    (),
                    {"enabled": True, "hosts": ["http://os"], "username": None, "password": None},
                )()

            class SearchConfiguration:
                def get_config(self):
                    return Cfg()

            monkeypatch.setattr("data.search.base.SearchConfiguration", SearchConfiguration)
            ts = build_search_backend("typesense")
            assert ts is not None
            osb = build_search_backend("opensearch")
            assert osb is not None
        finally:
            cleanup_fake_modules("typesense", "opensearchpy")
