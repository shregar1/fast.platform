"""Async engine helpers."""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from persistence.db.async_engine import (
    async_database_url_from_config,
    check_database_async,
    create_and_set_async_session_factory,
    create_async_session_factory,
    get_async_engine,
    get_async_engine_instance,
    get_async_session_factory,
)
from core.dtos import DBConfigurationDTO
from tests.persistence.db.abstraction import IDatabaseTests


class TestAsyncEngine(IDatabaseTests):
    """Represents the TestAsyncEngine class."""

    def test_async_database_url_postgres_derives_asyncpg(self):
        """Execute test_async_database_url_postgres_derives_asyncpg operation.

        Returns:
            The result of the operation.
        """
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

    def test_async_database_url_explicit_override(self):
        """Execute test_async_database_url_explicit_override operation.

        Returns:
            The result of the operation.
        """
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

    async def test_check_database_async_sqlite(self):
        """Execute test_check_database_async_sqlite operation.

        Returns:
            The result of the operation.
        """
        eng = create_async_engine("sqlite+aiosqlite:///:memory:")
        assert await check_database_async(eng) is True
        await eng.dispose()

    @patch("persistence.db.async_engine.create_async_engine")
    def test_get_async_engine_incomplete_raises(self, mock_create):
        """Execute test_get_async_engine_incomplete_raises operation.

        Args:
            mock_create: The mock_create parameter.

        Returns:
            The result of the operation.
        """
        with pytest.raises(RuntimeError, match="incomplete"):
            get_async_engine(DBConfigurationDTO())
        mock_create.assert_not_called()

    @patch("persistence.db.async_engine.DBConfiguration")
    def test_get_async_engine_uses_default_config(self, mock_db_cls):
        """Execute test_get_async_engine_uses_default_config operation.

        Args:
            mock_db_cls: The mock_db_cls parameter.

        Returns:
            The result of the operation.
        """
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
        with patch("persistence.db.async_engine.create_async_engine"):
            get_async_engine(None)
        mock_db_cls.assert_called()

    @patch("persistence.db.async_engine.create_async_session_factory")
    @patch("persistence.db.async_engine.get_async_engine")
    def test_create_and_set_async_session_factory_none_config_uses_singleton(
        self, mock_get_eng, mock_create_fac
    ):
        """Execute test_create_and_set_async_session_factory_none_config_uses_singleton operation.

        Args:
            mock_get_eng: The mock_get_eng parameter.
            mock_create_fac: The mock_create_fac parameter.

        Returns:
            The result of the operation.
        """
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
        with patch("persistence.db.async_engine.DBConfiguration", return_value=mock_db):
            out = create_and_set_async_session_factory(None)
        assert out is mock_fac
        mock_get_eng.assert_called_once_with(mock_conf)

    @patch("persistence.db.async_engine.create_async_engine")
    def test_get_async_engine_passes_pool_async(self, mock_create):
        """Execute test_get_async_engine_passes_pool_async operation.

        Args:
            mock_create: The mock_create parameter.

        Returns:
            The result of the operation.
        """
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

    @patch("persistence.db.async_engine.create_async_engine")
    def test_get_async_engine_passes_server_settings(self, mock_create):
        """Execute test_get_async_engine_passes_server_settings operation.

        Args:
            mock_create: The mock_create parameter.

        Returns:
            The result of the operation.
        """
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

    def test_async_read_replica_url_from_config(self):
        """Execute test_async_read_replica_url_from_config operation.

        Returns:
            The result of the operation.
        """
        from persistence.db.async_engine import async_read_replica_url_from_config

        cfg = DBConfigurationDTO(
            user_name="u",
            password="p",
            host="h",
            port=5432,
            database="d",
            connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
            read_replica_connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        )
        url = async_read_replica_url_from_config(cfg)
        assert url and "postgresql+asyncpg" in url

    @patch("persistence.db.async_engine.create_async_engine")
    def test_get_async_read_engine(self, mock_create):
        """Execute test_get_async_read_engine operation.

        Args:
            mock_create: The mock_create parameter.

        Returns:
            The result of the operation.
        """
        from persistence.db.async_engine import get_async_read_engine

        cfg = DBConfigurationDTO(
            user_name="u",
            password="p",
            host="h",
            port=5432,
            database="d",
            connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
            read_replica_connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        )
        mock_eng = MagicMock()
        mock_create.return_value = mock_eng
        out = get_async_read_engine(cfg)
        assert out is mock_eng
        mock_create.assert_called_once()

    def test_get_async_read_engine_none(self):
        """Execute test_get_async_read_engine_none operation.

        Returns:
            The result of the operation.
        """
        from persistence.db.async_engine import get_async_read_engine

        assert (
            get_async_read_engine(
                DBConfigurationDTO(
                    user_name="u",
                    password="p",
                    host="h",
                    port=5432,
                    database="d",
                    connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
                )
            )
            is None
        )

    def test_set_global_async_read_engine(self):
        """Execute test_set_global_async_read_engine operation.

        Returns:
            The result of the operation.
        """
        from persistence.db import async_engine as m

        mock_eng = MagicMock()
        try:
            m.set_global_async_read_engine(mock_eng)
            assert m.get_async_read_engine_instance() is mock_eng
        finally:
            m.set_global_async_read_engine(None)

    def test_async_database_url_sqlite_derived(self):
        """Execute test_async_database_url_sqlite_derived operation.

        Returns:
            The result of the operation.
        """
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

    def test_async_database_url_sqlite_two_slash_form(self):
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

    def test_async_database_url_unknown_driver_raises(self):
        """Execute test_async_database_url_unknown_driver_raises operation.

        Returns:
            The result of the operation.
        """
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

    def test_create_and_set_async_session_factory_returns_none_when_incomplete(self):
        """Execute test_create_and_set_async_session_factory_returns_none_when_incomplete operation.

        Returns:
            The result of the operation.
        """
        assert create_and_set_async_session_factory(DBConfigurationDTO()) is None

    @patch("persistence.db.async_engine.create_async_session_factory")
    @patch("persistence.db.async_engine.get_async_engine")
    def test_create_and_set_async_session_factory_sets_globals(self, mock_get_eng, mock_create_fac):
        """Execute test_create_and_set_async_session_factory_sets_globals operation.

        Args:
            mock_get_eng: The mock_get_eng parameter.
            mock_create_fac: The mock_create_fac parameter.

        Returns:
            The result of the operation.
        """
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
    async def test_check_database_async_connection_error(self):
        """Execute test_check_database_async_connection_error operation.

        Returns:
            The result of the operation.
        """

        class _CM:
            """Represents the _CM class."""

            async def __aenter__(self):
                """Execute __aenter__ operation.

                Returns:
                    The result of the operation.
                """
                raise RuntimeError("down")

            async def __aexit__(self, *a):
                """Execute __aexit__ operation.

                Returns:
                    The result of the operation.
                """
                return None

        eng = MagicMock()
        eng.connect = lambda: _CM()
        assert await check_database_async(eng) is False

    def test_create_async_session_factory_returns_callable(self):
        """Execute test_create_async_session_factory_returns_callable operation.

        Returns:
            The result of the operation.
        """
        eng = create_async_engine("sqlite+aiosqlite:///:memory:")
        fac = create_async_session_factory(eng)
        assert callable(fac)
