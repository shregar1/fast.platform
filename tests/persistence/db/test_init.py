"""Basic tests for db."""

from tests.persistence.db.abstraction import IDatabaseTests


class TestInit(IDatabaseTests):
    """Represents the TestInit class."""

    def test_import(self) -> None:
        """Execute test_import operation.

        Returns:
            The result of the operation.
        """
        import fast_platform.persistence.db as db

        assert db.__version__ == "0.1.0"
