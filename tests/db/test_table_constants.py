"""Tests for fast_db.table.Table constants."""

from fast_db.table import Table


def test_user_table_name():
    assert Table.USER == "user"
