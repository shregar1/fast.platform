"""Shared fixtures for db tests."""

import pytest

import persistence.db.async_engine as async_engine_mod


@pytest.fixture(autouse=True)
def _reset_async_globals():
    """Execute _reset_async_globals operation.

    Returns:
        The result of the operation.
    """
    async_engine_mod.set_global_async_engine(None)
    async_engine_mod.set_global_async_session_factory(None)
    yield
    async_engine_mod.set_global_async_engine(None)
    async_engine_mod.set_global_async_session_factory(None)
