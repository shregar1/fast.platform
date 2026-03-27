"""Tests for :mod:`persistence.datastores.abstraction`."""

from persistence.datastores.abstraction import IDatastores
from tests.persistence.datastores.abstraction import IDatastoresTests


class TestIDatastores(IDatastoresTests):
    """Represents the TestIDatastores class."""

    def test_marker_subclass(self) -> None:
        """Execute test_marker_subclass operation.

        Returns:
            The result of the operation.
        """

        class _P(IDatastores):
            """Represents the _P class."""

            pass

        assert issubclass(_P, IDatastores)
        assert isinstance(_P(), IDatastores)
