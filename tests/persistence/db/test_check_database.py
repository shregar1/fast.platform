"""Tests for check_database."""

from unittest.mock import MagicMock

from sqlalchemy import create_engine

from persistence.db import check_database
from tests.persistence.db.abstraction import IDatabaseTests


class TestCheckDatabase(IDatabaseTests):
    def test_check_database_ok_sqlite(self):
        eng = create_engine("sqlite:///:memory:")
        assert check_database(eng) is True

    def test_check_database_returns_false_on_connect_error(self):
        engine = MagicMock()
        engine.connect.side_effect = RuntimeError("unreachable")
        assert check_database(engine) is False
