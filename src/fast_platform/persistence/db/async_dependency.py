"""FastAPI dependency for async SQLAlchemy sessions.

Requires :func:`fast_db.async_engine.create_and_set_async_session_factory` at startup.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .async_engine import get_async_session_factory

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession


class AsyncDBDependency:
    """FastAPI dependency that yields an :class:`AsyncSession` per request.

    Usage::

        @router.get("/items")
        async def list_items(session: AsyncSession = Depends(AsyncDBDependency.session)):
            ...
    """

    @staticmethod
    async def session() -> AsyncGenerator[AsyncSession, None]:
        """Execute session operation.

        Returns:
            The result of the operation.
        """
        factory = get_async_session_factory()
        if factory is None:
            raise RuntimeError(
                "Async database session factory not initialized. "
                "Call create_and_set_async_session_factory() at startup."
            )
        async with factory() as session:
            yield session
