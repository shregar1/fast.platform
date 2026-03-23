from __future__ import annotations

"""Tests for :mod:`persistence.datastores.interfaces` ABC contracts."""
import pytest

from persistence.datastores.interfaces import (
    IDataStore,
    IDocumentStore,
    IKeyValueStore,
    IRelationalDatabase,
    ISearchStore,
    IWideColumnStore,
)
from tests.persistence.datastores.abstraction import IDatastoresTests


class TestInterfaces(IDatastoresTests):
    def test_idatastore_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            IDataStore()  # type: ignore[misc]

    def test_ikey_value_store_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            IKeyValueStore()  # type: ignore[misc]

    def test_idocument_store_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            IDocumentStore()  # type: ignore[misc]

    def test_irelational_database_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            IRelationalDatabase()  # type: ignore[misc]

    def test_iwide_column_store_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            IWideColumnStore()  # type: ignore[misc]

    def test_isearch_store_cannot_instantiate(self) -> None:
        with pytest.raises(TypeError):
            ISearchStore()  # type: ignore[misc]
