"""Tests for get_database_url with mocked configuration."""

from unittest.mock import MagicMock, patch

import pytest


def test_get_database_url_from_formatted_connection_string():
    from fast_db import get_database_url

    mock_cfg = MagicMock()
    mock_cfg.connection_string = "postgresql://{user_name}:{password}@{host}:{port}/{database}"
    mock_cfg.user_name = "u"
    mock_cfg.password = "p"
    mock_cfg.host = "localhost"
    mock_cfg.port = 5432
    mock_cfg.database = "db"

    with patch("fast_db.url.DBConfiguration") as DC:
        DC.return_value.get_config.return_value = mock_cfg
        url = get_database_url()
        assert "postgresql://" in url
        assert "u" in url
        assert "localhost" in url


def test_get_database_url_raw_string_fallback():
    from fast_db import get_database_url

    mock_cfg = MagicMock()
    mock_cfg.connection_string = "sqlite:///./test.db"
    mock_cfg.user_name = None
    mock_cfg.password = None
    mock_cfg.host = None
    mock_cfg.port = None
    mock_cfg.database = None

    with patch("fast_db.url.DBConfiguration") as DC:
        DC.return_value.get_config.return_value = mock_cfg
        assert get_database_url() == "sqlite:///./test.db"


def test_get_database_url_raises_when_incomplete():
    from fast_db import get_database_url

    mock_cfg = MagicMock()
    mock_cfg.connection_string = ""
    mock_cfg.user_name = None

    with patch("fast_db.url.DBConfiguration") as DC:
        DC.return_value.get_config.return_value = mock_cfg
        with pytest.raises(RuntimeError, match="incomplete"):
            get_database_url()
