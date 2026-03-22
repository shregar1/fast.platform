"""Sync engine passes pool settings from DBConfigurationDTO."""

from unittest.mock import MagicMock, patch

import pytest
from fast_core.config.dto import DBConfigurationDTO

from fast_db.engine import create_and_set_session, get_engine, sync_connect_args_for_url


def test_get_engine_passes_pool_kwargs():
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="localhost",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        pool_size=3,
        max_overflow=7,
        pool_timeout=15.0,
        pool_recycle=3600,
        pool_pre_ping=False,
    )
    with patch("fast_db.engine.create_engine") as mock_ce:
        get_engine(config)
        mock_ce.assert_called_once()
        _, kwargs = mock_ce.call_args
        assert kwargs["pool_size"] == 3
        assert kwargs["max_overflow"] == 7
        assert kwargs["pool_timeout"] == 15.0
        assert kwargs["pool_recycle"] == 3600
        assert kwargs["pool_pre_ping"] is False


def test_pool_recycle_omitted_when_none():
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="localhost",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        pool_recycle=None,
    )
    with patch("fast_db.engine.create_engine") as mock_ce:
        get_engine(config)
        _, kwargs = mock_ce.call_args
        assert "pool_recycle" not in kwargs


def test_get_engine_incomplete_raises():
    with pytest.raises(RuntimeError, match="incomplete"):
        get_engine(DBConfigurationDTO())


@patch("fast_db.engine.DBConfiguration")
def test_get_engine_uses_singleton_config(mock_db_cls):
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
    with patch("fast_db.engine.create_engine"):
        get_engine(None)
    mock_db_cls.assert_called()


@patch("fast_db.engine.set_global_session")
@patch("fast_db.engine.set_global_engine")
@patch("fast_db.engine.create_session_factory")
@patch("fast_db.engine.get_engine")
def test_create_and_set_session(mock_ge, mock_csf, mock_sge, mock_sgs):
    mock_eng = MagicMock()
    mock_ge.return_value = mock_eng
    mock_fac = MagicMock()
    mock_sess = MagicMock()
    mock_fac.return_value = mock_sess
    mock_csf.return_value = mock_fac
    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="h",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
    )
    out = create_and_set_session(config)
    assert out is mock_sess
    mock_sge.assert_called_once_with(mock_eng)
    mock_sgs.assert_called_once_with(mock_sess)


def test_create_and_set_session_returns_none_when_incomplete():
    assert create_and_set_session(DBConfigurationDTO()) is None


@patch("fast_db.engine.create_engine")
def test_get_engine_passes_postgres_connect_args(mock_ce):
    from fast_db.engine import get_engine

    config = DBConfigurationDTO(
        user_name="u",
        password="p",
        host="localhost",
        port=5432,
        database="d",
        connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        connection_name="primary-api",
        statement_timeout_seconds=2.5,
    )
    get_engine(config)
    mock_ce.assert_called_once()
    _, kwargs = mock_ce.call_args
    ca = kwargs["connect_args"]
    assert ca["application_name"] == "primary-api"
    assert "statement_timeout=2500" in ca["options"]


def test_sync_connect_args_sqlite_empty():
    cfg = DBConfigurationDTO(connection_name="x", statement_timeout_seconds=1.0)
    assert sync_connect_args_for_url("sqlite:///./a.db", cfg) == {}


def test_sync_connect_args_only_application_name():
    cfg = DBConfigurationDTO(connection_name="app")
    ca = sync_connect_args_for_url(
        "postgresql+psycopg2://u:p@h:5432/d",
        cfg,
    )
    assert ca["application_name"] == "app"
    assert "options" not in ca
