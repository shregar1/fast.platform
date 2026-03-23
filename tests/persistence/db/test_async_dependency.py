"""Tests for :mod:`persistence.db.async_dependency`."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.persistence.db.abstraction import IDatabaseTests


class TestAsyncDependency(IDatabaseTests):
    @pytest.mark.asyncio
    async def test_async_db_dependency_session(self):
        from persistence.db.async_dependency import AsyncDBDependency

        mock_session = MagicMock()
        factory = MagicMock()
        ctx = MagicMock()
        ctx.__aenter__ = AsyncMock(return_value=mock_session)
        ctx.__aexit__ = AsyncMock(return_value=None)
        factory.return_value = ctx
        with patch("persistence.db.async_dependency.get_async_session_factory", return_value=factory):
            async for s in AsyncDBDependency.session():
                assert s is mock_session
                break

    @pytest.mark.asyncio
    async def test_async_db_dependency_missing_factory(self):
        from persistence.db.async_dependency import AsyncDBDependency

        with patch("persistence.db.async_dependency.get_async_session_factory", return_value=None):
            gen = AsyncDBDependency.session()
            with pytest.raises(RuntimeError, match="Async database"):
                await gen.__anext__()
