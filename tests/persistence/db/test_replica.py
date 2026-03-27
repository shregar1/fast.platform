"""Module test_replica.py."""

from __future__ import annotations

"""Read-replica URL and engine helpers."""
from unittest.mock import MagicMock, patch

import pytest

from fast_platform.persistence.db.replica import (
    ReadDBDependency,
    create_and_set_read_session,
    create_read_session_factory,
    get_read_engine,
    read_replica_url_from_config,
)
from fast_platform.core.dtos import DBConfigurationDTO
from tests.persistence.db.abstraction import IDatabaseTests


class TestReplica(IDatabaseTests):
    """Represents the TestReplica class."""

    def test_read_replica_url_none_when_not_configured(self):
        """Execute test_read_replica_url_none_when_not_configured operation.

        Returns:
            The result of the operation.
        """
        cfg = DBConfigurationDTO(
            user_name="u",
            password="p",
            host="h",
            port=5432,
            database="d",
            connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        )
        assert read_replica_url_from_config(cfg) is None

    def test_read_replica_url_formats(self):
        """Execute test_read_replica_url_formats operation.

        Returns:
            The result of the operation.
        """
        cfg = DBConfigurationDTO(
            user_name="u",
            password="p",
            host="primary",
            port=5432,
            database="d",
            connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
            read_replica_connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
            read_replica_host="replica.internal",
        )
        url = read_replica_url_from_config(cfg)
        assert "replica.internal" in url
        assert "u" in url

    def test_get_read_engine_none_without_replica(self):
        """Execute test_get_read_engine_none_without_replica operation.

        Returns:
            The result of the operation.
        """
        assert get_read_engine(DBConfigurationDTO()) is None

    @patch("fast_platform.persistence.db.replica.create_engine")
    def test_get_read_engine_passes_connect_args(self, mock_ce):
        """Execute test_get_read_engine_passes_connect_args operation.

        Args:
            mock_ce: The mock_ce parameter.

        Returns:
            The result of the operation.
        """
        cfg = DBConfigurationDTO(
            user_name="u",
            password="p",
            host="h",
            port=5432,
            database="d",
            connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
            read_replica_connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
            connection_name="read-api",
            statement_timeout_seconds=5.0,
        )
        get_read_engine(cfg)
        mock_ce.assert_called_once()
        _, kwargs = mock_ce.call_args
        assert "connect_args" in kwargs
        assert kwargs["connect_args"]["application_name"] == "read-api"

    def test_create_read_session_factory_none(self):
        """Execute test_create_read_session_factory_none operation.

        Returns:
            The result of the operation.
        """
        assert create_read_session_factory(DBConfigurationDTO()) is None

    def test_read_db_dependency_raises_when_no_session(self):
        """Execute test_read_db_dependency_raises_when_no_session operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(RuntimeError, match="Read replica"):
            ReadDBDependency.derive()

    def test_read_db_dependency_returns_session(self):
        """Execute test_read_db_dependency_returns_session operation.

        Returns:
            The result of the operation.
        """
        mock_sess = MagicMock()
        with patch("fast_platform.persistence.db.replica.get_read_db_session", return_value=mock_sess):
            assert ReadDBDependency.derive() is mock_sess

    def test_get_read_engine_instance_after_create(self):
        """Execute test_get_read_engine_instance_after_create operation.

        Returns:
            The result of the operation.
        """
        from persistence.db.replica import get_read_engine_instance, set_global_read_engine

        mock_eng = MagicMock()
        try:
            set_global_read_engine(mock_eng)
            assert get_read_engine_instance() is mock_eng
        finally:
            set_global_read_engine(None)

    @patch("fast_platform.persistence.db.replica.get_read_engine")
    @patch("fast_platform.persistence.db.replica.create_session_factory")
    def test_create_and_set_read_session(self, mock_csf, mock_ge):
        """Execute test_create_and_set_read_session operation.

        Args:
            mock_csf: The mock_csf parameter.
            mock_ge: The mock_ge parameter.

        Returns:
            The result of the operation.
        """
        mock_eng = MagicMock()
        mock_ge.return_value = mock_eng
        mock_fac = MagicMock()
        mock_sess = MagicMock()
        mock_fac.return_value = mock_sess
        mock_csf.return_value = mock_fac
        cfg = DBConfigurationDTO(
            user_name="u",
            password="p",
            host="h",
            port=5432,
            database="d",
            connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
            read_replica_connection_string="postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{database}",
        )
        out = create_and_set_read_session(cfg)
        assert out is mock_sess
