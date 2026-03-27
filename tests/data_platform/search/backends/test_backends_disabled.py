"""Module test_backends_disabled.py."""

import types

from tests.data_platform.search.abstraction import ISearchTests


class TestBackendsDisabled(ISearchTests):
    """Represents the TestBackendsDisabled class."""

    def test_build_search_backend_returns_none_when_disabled(self, monkeypatch) -> None:
        """Execute test_build_search_backend_returns_none_when_disabled operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        from data.search import base as search_base

        class FakeCfg:
            """Represents the FakeCfg class."""

            def __init__(self):
                """Execute __init__ operation."""
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
