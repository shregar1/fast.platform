import builtins

import pytest

from tests.data_platform.search.abstraction import ISearchTests


class TestBackendsConstructorsMissing(ISearchTests):
    def test_backend_constructors_raise_runtime_error_when_dependency_missing(
        self, monkeypatch
    ) -> None:
        from data_platform.search.meilisearch_backend import MeilisearchBackend
        from data_platform.search.opensearch_backend import OpenSearchBackend
        from data_platform.search.typesense_backend import TypesenseBackend

        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            if name in {"meilisearch", "opensearchpy", "typesense"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            MeilisearchBackend(url="http://localhost:7700")
        with pytest.raises(RuntimeError):
            OpenSearchBackend(hosts=["http://localhost:9200"])
        with pytest.raises(RuntimeError):
            TypesenseBackend(host="localhost", port=8108, protocol="http", api_key=None)
