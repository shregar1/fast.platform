from __future__ import annotations

"""
Public API import tests for datastores.

Ensures every name in ``__all__`` resolves.
"""
import importlib

from tests.persistence.datastores.abstraction import IDatastoresTests

PACKAGE = "persistence.datastores"


class TestPublicApi(IDatastoresTests):
    def test_package_imports(self) -> None:
        m = importlib.import_module(PACKAGE)
        assert m is not None

    def test_public_exports_resolve(self) -> None:
        m = importlib.import_module(PACKAGE)
        for export_name in getattr(m, "__all__", ()):
            obj = getattr(m, export_name)
            assert obj is not None
