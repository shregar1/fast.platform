"""PostgreSQL advisory locks for safe concurrent migrations (multi-instance deploys).

Use around Alembic ``upgrade`` so only one process runs migrations at a time.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

from sqlalchemy import text

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection

# Default keys: 'FMVC' as int4 (customize per app if needed).
DEFAULT_MIGRATION_LOCK_KEY1 = 0x464D5643
DEFAULT_MIGRATION_LOCK_KEY2 = 0


@contextmanager
def advisory_migration_lock(
    connection: Connection,
    *,
    key1: int = DEFAULT_MIGRATION_LOCK_KEY1,
    key2: int = DEFAULT_MIGRATION_LOCK_KEY2,
) -> Iterator[None]:
    """Acquire ``pg_advisory_lock`` on *connection*, yield, then unlock.

    Raises:
        ValueError: If the dialect is not PostgreSQL.

    """
    if connection.dialect.name != "postgresql":
        raise ValueError("advisory_migration_lock only supports PostgreSQL connections")
    lock_sql = text("SELECT pg_advisory_lock(:k1, :k2)")
    unlock_sql = text("SELECT pg_advisory_unlock(:k1, :k2)")
    params = {"k1": key1, "k2": key2}
    connection.execute(lock_sql, params)
    try:
        yield
    finally:
        connection.execute(unlock_sql, params)


@contextmanager
def try_advisory_migration_lock(
    connection: Connection,
    *,
    key1: int = DEFAULT_MIGRATION_LOCK_KEY1,
    key2: int = DEFAULT_MIGRATION_LOCK_KEY2,
) -> Iterator[bool]:
    """Non-blocking ``pg_try_advisory_lock``: yields ``True`` if acquired.

    Unlocks in ``finally`` only when the lock was acquired.
    """
    if connection.dialect.name != "postgresql":
        raise ValueError("try_advisory_migration_lock only supports PostgreSQL connections")
    try_sql = text("SELECT pg_try_advisory_lock(:k1, :k2)")
    unlock_sql = text("SELECT pg_advisory_unlock(:k1, :k2)")
    params = {"k1": key1, "k2": key2}
    acquired = bool(connection.execute(try_sql, params).scalar())
    try:
        yield acquired
    finally:
        if acquired:
            connection.execute(unlock_sql, params)
