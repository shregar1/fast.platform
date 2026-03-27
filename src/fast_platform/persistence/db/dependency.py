"""FastAPI dependency for SQLAlchemy database session.

Use with FastAPI Depends(DBDependency.derive) to inject the shared session.
"""

from sqlalchemy.orm import Session

from .engine import get_db_session


class DBDependency:
    """FastAPI dependency provider for SQLAlchemy database sessions.

    Returns the shared session set at startup via engine.set_global_session().
    """

    @staticmethod
    def derive() -> Session:
        """Execute derive operation.

        Returns:
            The result of the operation.
        """
        session = get_db_session()
        if session is None:
            raise RuntimeError("Database session not initialized. Check startup and DB config.")
        return session
