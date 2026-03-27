"""Module test_backends_factory_import_error.py."""

import builtins
import sys
import types

from tests.data_platform.search.abstraction import ISearchTests


class TestBackendsFactoryImportError(ISearchTests):
    """Represents the TestBackendsFactoryImportError class."""

    def test_build_search_backend_import_error_returns_none(self, monkeypatch) -> None:
        """Execute test_build_search_backend_import_error_returns_none operation.

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
            """Execute _fail_specific_backend_import operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if (
                "meilisearch_backend" in name
                or "typesense_backend" in name
                or "opensearch_backend" in name
            ):
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fail_specific_backend_import)
        sys.modules.pop("fast_platform.data.search.meilisearch_backend", None)
        sys.modules.pop("fast_platform.data.search.typesense_backend", None)
        sys.modules.pop("fast_platform.data.search.opensearch_backend", None)
        assert search_base.build_search_backend("meilisearch") is None
        assert search_base.build_search_backend("typesense") is None
        assert search_base.build_search_backend("opensearch") is None
