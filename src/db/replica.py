"""
Read-replica URL and engine helpers (optional second connection for read-only work).

Configure ``read_replica_connection_string`` (and optional ``read_replica_host`` /
``read_replica_port``) on :class:`fast_core.config.dto.DBConfigurationDTO`.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from fast_core import DBConfiguration, DBConfigurationDTO

from .engine import _pool_kwargs, create_session_factory, sync_connect_args_for_url


class ReadDBDependency:
    """FastAPI dependency for the read-replica session (after :func:`create_and_set_read_session`)."""

    @staticmethod
    def derive() -> Session:
        session = get_read_db_session()
        if session is None:
            raise RuntimeError(
                "Read replica session not initialized. Call create_and_set_read_session at startup."
            )
        return session

_global_read_engine: Optional[Engine] = None
_global_read_session: Optional[Session] = None


def _primary_config_complete(config: DBConfigurationDTO) -> bool:
    return bool(
        config.user_name
        and config.password
        and config.host
        and config.port
        and config.database
        and config.connection_string
    )


def read_replica_url_from_config(config: DBConfigurationDTO) -> Optional[str]:
    """
    Build the read-replica DSN when ``read_replica_connection_string`` is set.

    Returns ``None`` if replica is not configured or primary credentials are incomplete.
    """
    tmpl = (config.read_replica_connection_string or "").strip()
    if not tmpl or not _primary_config_complete(config):
        return None
    host = config.read_replica_host or config.host
    port = config.read_replica_port if config.read_replica_port is not None else config.port
    return tmpl.format(
        user_name=config.user_name,
        password=config.password,
        host=host,
        port=port,
        database=config.database,
    )


def get_read_engine(config: Optional[DBConfigurationDTO] = None) -> Optional[Engine]:
    """
    Create a sync :class:`~sqlalchemy.engine.Engine` for the read replica, or ``None``.

    Uses the same pool and PostgreSQL ``connect_args`` as :func:`get_engine`.
    """
    if config is None:
        config = DBConfiguration().get_config()
    url = read_replica_url_from_config(config)
    if not url:
        return None
    ca = sync_connect_args_for_url(url, config)
    pool = _pool_kwargs(config)
    if ca:
        return create_engine(url, connect_args=ca, **pool)
    return create_engine(url, **pool)


def create_read_session_factory(
    config: Optional[DBConfigurationDTO] = None,
) -> Optional[sessionmaker[Session]]:
    """Return a :class:`sessionmaker` for the read replica, or ``None`` if not configured."""
    eng = get_read_engine(config)
    if eng is None:
        return None
    return create_session_factory(eng)


def set_global_read_engine(engine: Optional[Engine]) -> None:
    global _global_read_engine
    _global_read_engine = engine


def set_global_read_session(session: Optional[Session]) -> None:
    global _global_read_session
    _global_read_session = session


def get_read_db_session() -> Optional[Session]:
    """Session from :func:`create_and_set_read_session`, if any."""
    return _global_read_session


def get_read_engine_instance() -> Optional[Engine]:
    return _global_read_engine


def create_and_set_read_session(
    config: Optional[DBConfigurationDTO] = None,
) -> Optional[Session]:
    """
    Build read engine + session, store globals for :func:`get_read_db_session`.

    Returns ``None`` if replica is not configured or primary config is incomplete.
    """
    if config is None:
        config = DBConfiguration().get_config()
    eng = get_read_engine(config)
    if eng is None:
        return None
    set_global_read_engine(eng)
    fac = create_session_factory(eng)
    sess: Session = fac()
    set_global_read_session(sess)
    return sess
