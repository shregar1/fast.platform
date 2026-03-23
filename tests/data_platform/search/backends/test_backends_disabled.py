import types

from tests.data_platform.search.abstraction import ISearchTests


class TestBackendsDisabled(ISearchTests):
    def test_build_search_backend_returns_none_when_disabled(self, monkeypatch) -> None:
        from data_platform.search import base as search_base

        class FakeCfg:
            def __init__(self):
                self.meilisearch = types.SimpleNamespace(
                    enabled=False, url="http://localhost:7700", api_key=None
                )
                self.typesense = types.SimpleNamespace(enabled=False)
                self.opensearch = types.SimpleNamespace(enabled=False)

        monkeypatch.setattr(
            search_base,
            "SearchConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        assert search_base.build_search_backend("meilisearch") is None
        assert search_base.build_search_backend("typesense") is None
        assert search_base.build_search_backend("opensearch") is None
