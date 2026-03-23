"""Tests for :mod:`persistence.datastores.abstraction`."""

from persistence.datastores.abstraction import IDatastores
from tests.persistence.datastores.abstraction import IDatastoresTests


class TestIDatastores(IDatastoresTests):
    def test_marker_subclass(self) -> None:
        class _P(IDatastores):
            pass

        assert issubclass(_P, IDatastores)
        assert isinstance(_P(), IDatastores)
