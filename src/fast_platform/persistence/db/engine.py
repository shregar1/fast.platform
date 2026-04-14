"""Database engine and session factory.

Creates SQLAlchemy engine and session from fast_platform DBConfiguration.
The application should call create_and_set_session() at startup (or create_engine +
create_session + set_global_session), then use get_db_session() or DBDependency.
"""

from .constants import POSTGRESQL_DRIVER, DEFAULT_SQLITE_URL_PREFIX, INCOMPLETE_DB_CONFIG_ERROR
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from fast_platform import DBConfiguration, DBConfigurationDTO


def sync_connect_args_for_url(url: str, config: DBConfigurationDTO) -> dict:
    """PostgreSQL ``connect_args``: ``application_name`` and ``statement_timeout`` (via ``options``).

    No-op for non-PostgreSQL URLs.
    """
    if "postgresql" not in url.lower():
        return {}
    opts: dict = {}
    parts: list[str] = []
    if config.connection_name:
        opts["application_name"] = config.connection_name
    if config.statement_timeout_seconds is not None:
        ms = int(config.statement_timeout_seconds * 1000)
        parts.append(f"-c statement_timeout={ms}")
    if parts:
        opts["options"] = " ".join(parts)
    return opts


_global_session: Optional[Session] = None
_engine: Optional[Engine] = None


def _pool_kwargs(config: DBConfigurationDTO) -> dict:
    """Arguments passed to ``create_engine`` / ``create_async_engine`` for pooling."""
    kw: dict = {
        "pool_size": config.pool_size,
        "max_overflow": config.max_overflow,
        "pool_timeout": config.pool_timeout,
        "pool_pre_ping": config.pool_pre_ping,
    }
    if config.pool_recycle is not None:
        kw["pool_recycle"] = config.pool_recycle
    return kw


def get_engine(config: Optional[DBConfigurationDTO] = None) -> Engine:
    """Build a SQLAlchemy Engine from DB configuration.

    Args:
        config: Database config DTO. If None, uses DBConfiguration().get_config().

    Returns:
        SQLAlchemy Engine.

    Raises:
        RuntimeError: If config is incomplete.

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
    url = config.connection_string.format(
        user_name=config.user_name,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.database,
    )
    ca = sync_connect_args_for_url(url, config)
    pool = _pool_kwargs(config)
    if ca:
        return create_engine(url, connect_args=ca, **pool)
    return create_engine(url, **pool)


def create_session_factory(engine: Engine) -> sessionmaker:
    """Create a sessionmaker bound to the given engine."""
    return sessionmaker[Session](bind=engine)


def set_global_session(session: Session) -> None:
    """Set the global session used by get_db_session() and DBDependency."""
    global _global_session
    _global_session = session


def set_global_engine(engine: Engine) -> None:
    """Store engine reference (optional, for cleanup)."""
    global _engine
    _engine = engine


def get_db_session() -> Optional[Session]:
    """Return the global database session, or None if not initialized."""
    return _global_session


def check_database(engine: Engine) -> bool:
    """Return True if the database accepts a trivial query (``SELECT 1``).

    Use for readiness/liveness probes without raising from route handlers.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def create_and_set_session(config: Optional[DBConfigurationDTO] = None) -> Optional[Session]:
    """Create engine and session from config, set as global, and return the session.
    Returns None if config is incomplete (no session created).
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
    eng = get_engine(config)
    set_global_engine(eng)
    factory = create_session_factory(eng)
    session: Session = factory()
    set_global_session(session)
    return session
