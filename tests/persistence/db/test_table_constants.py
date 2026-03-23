"""Tests for db.table.Table constants."""

from persistence.db.table import Table
from tests.persistence.db.abstraction import IDatabaseTests


class TestTableConstants(IDatabaseTests):
    def test_user_table_name(self):
        assert Table.USER == "user"
