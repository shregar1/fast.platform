"""Tests for db.table.Table constants."""

from db.table import Table


def test_user_table_name():
    assert Table.USER == "user"
