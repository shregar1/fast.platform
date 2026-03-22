"""Tests for :mod:`datastores.abstraction`."""
from tests.persistence.datastores.abstraction import IDatastoresTests


from datastores.abstraction import IDatastores


class TestIDatastores(IDatastoresTests):
    def test_marker_subclass(self) -> None:
        class _P(IDatastores):
            pass

        assert issubclass(_P, IDatastores)
        assert isinstance(_P(), IDatastores)
