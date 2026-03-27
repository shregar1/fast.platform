"""Tests for db.table.Table constants."""

from fast_platform.persistence.db.table import Table
from tests.persistence.db.abstraction import IDatabaseTests


class TestTableConstants(IDatabaseTests):
    """Represents the TestTableConstants class."""

    def test_user_table_name(self):
        """Execute test_user_table_name operation.

        Returns:
            The result of the operation.
        """
        assert Table.USER == "user"
