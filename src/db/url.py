"""
Database URL helper for Alembic and other tools.

Uses fast_core DBConfiguration; ensure FASTMVC_CONFIG_BASE is set
so config/db/config.json is found.
"""

from fast_core import DBConfiguration


def get_database_url() -> str:
    """
    Build SQLAlchemy database URL from DB configuration.

    Returns:
        Connection URL string.

    Raises:
        RuntimeError: If config is incomplete for migrations.
    """
    db_config = DBConfiguration().get_config()
    if db_config.connection_string:
        try:
            return db_config.connection_string.format(
                user_name=db_config.user_name,
                password=db_config.password,
                host=db_config.host,
                port=db_config.port,
                database=db_config.database,
            )
        except Exception:
            pass
        if db_config.connection_string:
            return db_config.connection_string
    raise RuntimeError(
        "Database configuration is incomplete for Alembic. "
        "Please update config/db/config.json with valid connection details."
    )
