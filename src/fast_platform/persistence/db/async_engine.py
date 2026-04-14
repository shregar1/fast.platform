from __future__ import annotations
"""Async SQLAlchemy engine and session factory (SQLAlchemy 2.x asyncio).

Install a driver for your database, e.g.::

    pip install 'fast_db[async]'   # asyncpg for PostgreSQL

For SQLite async tests, ``aiosqlite`` is typical::

    pip install aiosqlite

Use :func:`create_and_set_async_session_factory` at startup, then
:class:`fast_db.async_dependency.AsyncDBDependency` with FastAPI.
"""

from .constants import POSTGRESQL_DRIVER, DEFAULT_SQLITE_URL_PREFIX, INCOMPLETE_DB_CONFIG_ERROR

from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fast_platform import DBConfiguration, DBConfigurationDTO

from .engine import _pool_kwargs

_global_async_engine: Optional[AsyncEngine] = None
_global_async_read_engine: Optional[AsyncEngine] = None


def sync_url_to_async_url(sync_url: str) -> str:
    """Derive async driver URL from a sync SQLAlchemy URL (same rules as primary async)."""
    if "postgresql+psycopg2" in sync_url:
        return sync_url.replace("postgresql+psycopg2", POSTGRESQL_DRIVER, 1)
    if sync_url.startswith("sqlite"):
        if sync_url.startswith("sqlite:///"):
            return DEFAULT_SQLITE_URL_PREFIX + sync_url[len("sqlite:///") :]
        return sync_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    raise ValueError(
        "Could not derive async URL from sync URL. Set async_connection_string in config/db/config.json."
    )


def async_connect_args_for_url(url: str, config: DBConfigurationDTO) -> dict:
    """Asyncpg ``server_settings``: ``application_name`` and ``statement_timeout`` (ms)."""
    if "postgresql" not in url.lower():
        return {}
    settings: dict[str, str] = {}
    if config.connection_name:
        settings["application_name"] = config.connection_name
    if config.statement_timeout_seconds is not None:
        ms = int(config.statement_timeout_seconds * 1000)
        settings["statement_timeout"] = str(ms)
    if not settings:
        return {}
    return {"server_settings": settings}


_global_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def _format_sync_url(config: DBConfigurationDTO) -> str:
    """Execute _format_sync_url operation.

    Args:
        config: The config parameter.

    Returns:
        The result of the operation.
    """
    return config.connection_string.format(
        user_name=config.user_name,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.database,
    )


def async_database_url_from_config(config: DBConfigurationDTO) -> str:
    """Build the async SQLAlchemy URL: use ``async_connection_string`` when set,
    otherwise derive from the sync URL (PostgreSQL → asyncpg, SQLite → aiosqlite).
    """
    if config.async_connection_string.strip():
        return config.async_connection_string.format(
            user_name=config.user_name,
            password=config.password,
            host=config.host,
            port=config.port,
            database=config.database,
        )
    sync = _format_sync_url(config)
    return sync_url_to_async_url(sync)


def get_async_engine(config: Optional[DBConfigurationDTO] = None) -> AsyncEngine:
    """Build an async :class:`AsyncEngine` from DB configuration.

    Raises:
        RuntimeError: If required fields are missing (same rules as sync :func:`get_engine`).
        ValueError: If async URL cannot be resolved.

    """
    if config is None:
        config = DBConfiguration().get_config()
    if not (
        config.user_name
        and config.password
        and config.host
        and config.port
        and config.database
        and config.connection_string
    ):
        raise RuntimeError(
            "Database configuration is incomplete. "
            "Set user_name, password, host, port, database, and connection_string."
        )
    url = async_database_url_from_config(config)
    ca = async_connect_args_for_url(url, config)
    pool = _pool_kwargs(config)
    if ca:
        return create_async_engine(url, connect_args=ca, **pool)
    return create_async_engine(url, **pool)


def create_async_session_factory(
    engine: AsyncEngine,
    *,
    expire_on_commit: bool = False,
) -> async_sessionmaker[AsyncSession]:
    """Create an :class:`async_sessionmaker` bound to *engine*."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=expire_on_commit,
    )


def set_global_async_engine(engine: Optional[AsyncEngine]) -> None:
    """Execute set_global_async_engine operation.

    Args:
        engine: The engine parameter.

    Returns:
        The result of the operation.
    """
    global _global_async_engine
    _global_async_engine = engine


def set_global_async_session_factory(
    factory: Optional[async_sessionmaker[AsyncSession]],
) -> None:
    """Execute set_global_async_session_factory operation.

    Args:
        factory: The factory parameter.

    Returns:
        The result of the operation.
    """
    global _global_async_session_factory
    _global_async_session_factory = factory


def get_async_session_factory() -> Optional[async_sessionmaker[AsyncSession]]:
    """Execute get_async_session_factory operation.

    Returns:
        The result of the operation.
    """
    return _global_async_session_factory


def get_async_engine_instance() -> Optional[AsyncEngine]:
    """Return the engine set by :func:`create_and_set_async_session_factory`, if any."""
    return _global_async_engine


def async_read_replica_url_from_config(config: DBConfigurationDTO) -> Optional[str]:
    """Async URL for read replica (derived from sync replica URL when configured)."""
    from .replica import read_replica_url_from_config

    sync_u = read_replica_url_from_config(config)
    if not sync_u:
        return None
    return sync_url_to_async_url(sync_u)


def get_async_read_engine(
    config: Optional[DBConfigurationDTO] = None,
) -> Optional[AsyncEngine]:
    """Async engine for read replica, or ``None`` if not configured."""
    if config is None:
        config = DBConfiguration().get_config()
    url = async_read_replica_url_from_config(config)
    if not url:
        return None
    ca = async_connect_args_for_url(url, config)
    pool = _pool_kwargs(config)
    if ca:
        return create_async_engine(url, connect_args=ca, **pool)
    return create_async_engine(url, **pool)


def set_global_async_read_engine(engine: Optional[AsyncEngine]) -> None:
    """Execute set_global_async_read_engine operation.

    Args:
        engine: The engine parameter.

    Returns:
        The result of the operation.
    """
    global _global_async_read_engine
    _global_async_read_engine = engine


def get_async_read_engine_instance() -> Optional[AsyncEngine]:
    """Execute get_async_read_engine_instance operation.

    Returns:
        The result of the operation.
    """
    return _global_async_read_engine


def create_and_set_async_session_factory(
    config: Optional[DBConfigurationDTO] = None,
    *,
    expire_on_commit: bool = False,
) -> Optional[async_sessionmaker[AsyncSession]]:
    """Create async engine + session factory, store as globals, return the factory.

    Returns ``None`` if config is incomplete (same as sync session helper).
    """
    if config is None:
        config = DBConfiguration().get_config()
    if not (
        config.user_name
        and config.password
        and config.host
        and config.port
        and config.database
        and config.connection_string
    ):
        return None
    eng = get_async_engine(config)
    set_global_async_engine(eng)
    fac = create_async_session_factory(eng, expire_on_commit=expire_on_commit)
    set_global_async_session_factory(fac)
    return fac


async def check_database_async(engine: AsyncEngine) -> bool:
    """Return True if ``SELECT 1`` succeeds on *engine*."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
