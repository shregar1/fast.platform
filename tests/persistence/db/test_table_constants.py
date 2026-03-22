"""Tests for db.table.Table constants."""
from tests.persistence.db.abstraction import IDatabaseTests

from db.table import Table

class TestTableConstants(IDatabaseTests):

    def test_user_table_name(self):
        assert Table.USER == 'user'
