"""Basic tests for db."""

from tests.persistence.db.abstraction import IDatabaseTests


class TestInit(IDatabaseTests):
    def test_import(self) -> None:
        import persistence.db as db

        assert db.__version__ == "0.1.0"
