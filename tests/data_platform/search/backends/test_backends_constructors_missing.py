"""Module test_backends_constructors_missing.py."""

import builtins

import pytest

from tests.data_platform.search.abstraction import ISearchTests


class TestBackendsConstructorsMissing(ISearchTests):
    """Represents the TestBackendsConstructorsMissing class."""

    def test_backend_constructors_raise_runtime_error_when_dependency_missing(
        self, monkeypatch
    ) -> None:
        """Execute test_backend_constructors_raise_runtime_error_when_dependency_missing operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        from fast_platform.data.search.meilisearch_backend import MeilisearchBackend
        from fast_platform.data.search.opensearch_backend import OpenSearchBackend
        from fast_platform.data.search.typesense_backend import TypesenseBackend

        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            """Execute _deny_import operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
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
