import builtins
import sys
import types

from tests.data_platform.search.abstraction import ISearchTests


class TestBackendsFactoryImportError(ISearchTests):
    def test_build_search_backend_import_error_returns_none(self, monkeypatch) -> None:
        from data.search import base as search_base

        class FakeCfg:
            def __init__(self):
                self.meilisearch = types.SimpleNamespace(
                    enabled=True, url="http://localhost:7700", api_key="k"
                )
                self.typesense = types.SimpleNamespace(
                    enabled=True, host="localhost", port=8108, protocol="http", api_key="k"
                )
                self.opensearch = types.SimpleNamespace(
                    enabled=True, hosts=["http://localhost:9200"], username=None, password=None
                )

        monkeypatch.setattr(
            search_base,
            "SearchConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        real_import = builtins.__import__

        def _fail_specific_backend_import(name, *args, **kwargs):
            if (
                "meilisearch_backend" in name
                or "typesense_backend" in name
                or "opensearch_backend" in name
            ):
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fail_specific_backend_import)
        sys.modules.pop("data.search.meilisearch_backend", None)
        sys.modules.pop("data.search.typesense_backend", None)
        sys.modules.pop("data.search.opensearch_backend", None)
        assert search_base.build_search_backend("meilisearch") is None
        assert search_base.build_search_backend("typesense") is None
        assert search_base.build_search_backend("opensearch") is None
