"""get_database_url."""

from unittest.mock import MagicMock, patch

import pytest

from fast_db.url import get_database_url


@patch("fast_db.url.DBConfiguration")
def test_get_database_url_formatted(mock_cls):
    cfg = MagicMock()
    cfg.connection_string = "postgresql://{user_name}@{host}:{port}/{database}"
    cfg.user_name = "u"
    cfg.password = "p"
    cfg.host = "h"
    cfg.port = 5432
    cfg.database = "d"
    mock_inst = MagicMock()
    mock_inst.get_config.return_value = cfg
    mock_cls.return_value = mock_inst
    url = get_database_url()
    assert "postgresql://" in url
    assert "u" in url


@patch("fast_db.url.DBConfiguration")
def test_get_database_url_fallback_when_format_fails(mock_cls):
    cfg = MagicMock()
    cfg.connection_string = "postgresql://{bad_placeholder"
    cfg.user_name = "u"
    cfg.password = "p"
    cfg.host = "h"
    cfg.port = 5432
    cfg.database = "d"
    mock_inst = MagicMock()
    mock_inst.get_config.return_value = cfg
    mock_cls.return_value = mock_inst
    assert get_database_url() == cfg.connection_string


@patch("fast_db.url.DBConfiguration")
def test_get_database_url_raises_when_empty(mock_cls):
    cfg = MagicMock()
    cfg.connection_string = ""
    mock_inst = MagicMock()
    mock_inst.get_config.return_value = cfg
    mock_cls.return_value = mock_inst
    with pytest.raises(RuntimeError, match="incomplete"):
        get_database_url()
