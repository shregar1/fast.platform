"""Module test_migration_lock.py."""

from __future__ import annotations

"""PostgreSQL advisory migration locks."""
from unittest.mock import MagicMock

import pytest

from persistence.db.migration_lock import advisory_migration_lock, try_advisory_migration_lock
from tests.persistence.db.abstraction import IDatabaseTests


class TestMigrationLock(IDatabaseTests):
    """Represents the TestMigrationLock class."""

    def test_advisory_lock_rejects_non_postgres(self):
        """Execute test_advisory_lock_rejects_non_postgres operation.

        Returns:
            The result of the operation.
        """
        conn = MagicMock()
        conn.dialect.name = "sqlite"
        with pytest.raises(ValueError, match="PostgreSQL"):
            with advisory_migration_lock(conn):
                pass

    def test_advisory_lock_acquires_and_releases(self):
        """Execute test_advisory_lock_acquires_and_releases operation.

        Returns:
            The result of the operation.
        """
        conn = MagicMock()
        conn.dialect.name = "postgresql"
        with advisory_migration_lock(conn):
            pass
        assert conn.execute.call_count == 2

    def test_try_lock_rejects_non_postgres(self):
        """Execute test_try_lock_rejects_non_postgres operation.

        Returns:
            The result of the operation.
        """
        conn = MagicMock()
        conn.dialect.name = "mysql"
        with pytest.raises(ValueError, match="PostgreSQL"):
            with try_advisory_migration_lock(conn):
                pass

    def test_try_lock_yields_true_and_unlocks(self):
        """Execute test_try_lock_yields_true_and_unlocks operation.

        Returns:
            The result of the operation.
        """
        conn = MagicMock()
        conn.dialect.name = "postgresql"
        exec_result = MagicMock()
        exec_result.scalar.return_value = True
        conn.execute.return_value = exec_result
        with try_advisory_migration_lock(conn) as acquired:
            assert acquired is True
        assert conn.execute.call_count == 2

    def test_try_lock_false_skips_unlock(self):
        """Execute test_try_lock_false_skips_unlock operation.

        Returns:
            The result of the operation.
        """
        conn = MagicMock()
        conn.dialect.name = "postgresql"
        exec_result = MagicMock()
        exec_result.scalar.return_value = False
        conn.execute.return_value = exec_result
        with try_advisory_migration_lock(conn) as acquired:
            assert acquired is False
        assert conn.execute.call_count == 1
