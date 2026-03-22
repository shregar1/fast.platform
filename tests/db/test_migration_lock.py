"""PostgreSQL advisory migration locks."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from db.migration_lock import (
    advisory_migration_lock,
    try_advisory_migration_lock,
)


def test_advisory_lock_rejects_non_postgres():
    conn = MagicMock()
    conn.dialect.name = "sqlite"
    with pytest.raises(ValueError, match="PostgreSQL"):
        with advisory_migration_lock(conn):
            pass


def test_advisory_lock_acquires_and_releases():
    conn = MagicMock()
    conn.dialect.name = "postgresql"
    with advisory_migration_lock(conn):
        pass
    assert conn.execute.call_count == 2


def test_try_lock_rejects_non_postgres():
    conn = MagicMock()
    conn.dialect.name = "mysql"
    with pytest.raises(ValueError, match="PostgreSQL"):
        with try_advisory_migration_lock(conn):
            pass


def test_try_lock_yields_true_and_unlocks():
    conn = MagicMock()
    conn.dialect.name = "postgresql"
    exec_result = MagicMock()
    exec_result.scalar.return_value = True
    conn.execute.return_value = exec_result
    with try_advisory_migration_lock(conn) as acquired:
        assert acquired is True
    assert conn.execute.call_count == 2


def test_try_lock_false_skips_unlock():
    conn = MagicMock()
    conn.dialect.name = "postgresql"
    exec_result = MagicMock()
    exec_result.scalar.return_value = False
    conn.execute.return_value = exec_result
    with try_advisory_migration_lock(conn) as acquired:
        assert acquired is False
    assert conn.execute.call_count == 1
