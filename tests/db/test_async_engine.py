"""Async engine helpers."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fast_core.config.dto import DBConfigurationDTO
from sqlalchemy.ext.asyncio import create_async_engine

import fast_db.async_engine as async_engine_mod
from fast_db.async_engine import (
    async_database_url_from_config,
    check_database_async,
    create_and_set_async_session_factory,
    create_async_session_factory,
    get_async_engine,
    get_async_engine_instance,
    get_async_session_factory,
)


@pytest.fixture(autouse=True)
def _reset_async_globals():
    async_engine_mod.set_global_async_engine(None)
    async_engine_mod.set_global_async_session_factory(None)
    yield
    async_engine_mod.set_global_async_engine(None)
    async_engine_mod.set_global_async_session_factory(None)


def test_async_database_url_postgres_derives_asyncpg():
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
    )
    url = async_database_url_from_config(config)
    assert "postgresql+asyncpg" in url
    assert "u" in url and "d" in url


def test_async_database_url_explicit_override():
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        async_connection_string="postgresql+asyncpg://{user_name}:{password}@{host}:{port}/{database}",
    )
    url = async_database_url_from_config(config)
    assert url.startswith("postgresql+asyncpg://")


async def test_check_database_async_sqlite():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    assert await check_database_async(eng) is True
    await eng.dispose()


@patch("fast_db.async_engine.create_async_engine")
def test_get_async_engine_incomplete_raises(mock_create):
    with pytest.raises(RuntimeError, match="incomplete"):
        get_async_engine(DBConfigurationDTO())
    mock_create.assert_not_called()


@patch("fast_db.async_engine.DBConfiguration")
def test_get_async_engine_uses_default_config(mock_db_cls):
    mock_conf = MagicMock()
    mock_conf.get_config.return_value = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
    )
    mock_db_cls.return_value = mock_conf
    with patch("fast_db.async_engine.create_async_engine"):
        get_async_engine(None)
    mock_db_cls.assert_called()


@patch("fast_db.async_engine.create_async_session_factory")
@patch("fast_db.async_engine.get_async_engine")
def test_create_and_set_async_session_factory_none_config_uses_singleton(
    mock_get_eng,
    mock_create_fac,
):
    mock_conf = MagicMock()
    mock_conf.get_config.return_value = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
    )
    mock_db = MagicMock()
    mock_db.get_config.return_value = mock_conf
    mock_eng = MagicMock()
    mock_get_eng.return_value = mock_eng
    mock_fac = MagicMock()
    mock_create_fac.return_value = mock_fac

    with patch("fast_db.async_engine.DBConfiguration", return_value=mock_db):
        out = create_and_set_async_session_factory(None)
    assert out is mock_fac
    mock_get_eng.assert_called_once_with(mock_conf)


@patch("fast_db.async_engine.create_async_engine")
def test_get_async_engine_passes_pool_async(mock_create):
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        pool_size=2,
        pool_recycle=100,
    )
    get_async_engine(config)
    mock_create.assert_called_once()
    _, kwargs = mock_create.call_args
    assert kwargs["pool_size"] == 2
    assert kwargs["pool_recycle"] == 100


@patch("fast_db.async_engine.create_async_engine")
def test_get_async_engine_passes_server_settings(mock_create):
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        connection_name="async-primary",
        statement_timeout_seconds=3.0,
    )
    get_async_engine(config)
    _, kwargs = mock_create.call_args
    ss = kwargs["connect_args"]["server_settings"]
    assert ss["application_name"] == "async-primary"
    assert ss["statement_timeout"] == "3000"


def test_async_read_replica_url_from_config():
    from fast_db.async_engine import async_read_replica_url_from_config

    cfg = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        read_replica_connection_string=(
            "postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}"
        ),
    )
    url = async_read_replica_url_from_config(cfg)
    assert url and "postgresql+asyncpg" in url


@patch("fast_db.async_engine.create_async_engine")
def test_get_async_read_engine(mock_create):
    from fast_db.async_engine import get_async_read_engine

    cfg = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        read_replica_connection_string=(
            "postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}"
        ),
    )
    mock_eng = MagicMock()
    mock_create.return_value = mock_eng
    out = get_async_read_engine(cfg)
    assert out is mock_eng
    mock_create.assert_called_once()


def test_get_async_read_engine_none():
    from fast_db.async_engine import get_async_read_engine

    assert (
        get_async_read_engine(
            DBConfigurationDTO(
                user_name="u",
                password="p",
                host="h",
                port=5432,
                database="d",
                connection_string=(
                    "postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}"
                ),
            )
        )
        is None
    )


def test_set_global_async_read_engine():
    from fast_db import async_engine as m

    mock_eng = MagicMock()
    try:
        m.set_global_async_read_engine(mock_eng)
        assert m.get_async_read_engine_instance() is mock_eng
    finally:
        m.set_global_async_read_engine(None)


def test_async_database_url_sqlite_derived():
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="app",
        connection_string="sqlite:///./{database}.db",
    )
    url = async_database_url_from_config(config)
    assert url.startswith("sqlite+aiosqlite:///./")
    assert "app.db" in url


def test_async_database_url_sqlite_two_slash_form():
    """Covers branch: sqlite:// without sqlite:///."""
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="localhost",
        port=5432,
        database="d",
        connection_string="sqlite://{host}/db.sqlite",
    )
    url = async_database_url_from_config(config)
    assert "sqlite+aiosqlite" in url


def test_async_database_url_unknown_driver_raises():
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="mysql+pymysql://{user_name}:{password}@{host}:{port}/{database}",
    )
    with pytest.raises(ValueError, match="async URL|async_connection_string"):
        async_database_url_from_config(config)


def test_create_and_set_async_session_factory_returns_none_when_incomplete():
    assert create_and_set_async_session_factory(DBConfigurationDTO()) is None


@patch("fast_db.async_engine.create_async_session_factory")
@patch("fast_db.async_engine.get_async_engine")
def test_create_and_set_async_session_factory_sets_globals(mock_get_eng, mock_create_fac):
    mock_eng = MagicMock()
    mock_get_eng.return_value = mock_eng
    mock_fac = MagicMock()
    mock_create_fac.return_value = mock_fac
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
    )
    out = create_and_set_async_session_factory(config, expire_on_commit=True)
    assert out is mock_fac
    assert get_async_engine_instance() is mock_eng
    assert get_async_session_factory() is mock_fac
    mock_create_fac.assert_called_once_with(mock_eng, expire_on_commit=True)


@pytest.mark.asyncio
async def test_check_database_async_connection_error():
    class _CM:
        async def __aenter__(self):
            raise RuntimeError("down")

        async def __aexit__(self, *a):
            return None

    eng = MagicMock()
    eng.connect = lambda: _CM()
    assert await check_database_async(eng) is False


def test_create_async_session_factory_returns_callable():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    fac = create_async_session_factory(eng)
    assert callable(fac)


@pytest.mark.asyncio
async def test_async_db_dependency_session():
    from fast_db.async_dependency import AsyncDBDependency

    mock_session = MagicMock()
    factory = MagicMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_session)
    ctx.__aexit__ = AsyncMock(return_value=None)
    factory.return_value = ctx

    with patch(
        "fast_db.async_dependency.get_async_session_factory",
        return_value=factory,
    ):
        async for s in AsyncDBDependency.session():
            assert s is mock_session
            break


@pytest.mark.asyncio
async def test_async_db_dependency_missing_factory():
    from fast_db.async_dependency import AsyncDBDependency

    with patch(
        "fast_db.async_dependency.get_async_session_factory",
        return_value=None,
    ):
        gen = AsyncDBDependency.session()
        with pytest.raises(RuntimeError, match="Async database"):
            await gen.__anext__()
