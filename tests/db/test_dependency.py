"""DBDependency."""

from unittest.mock import MagicMock, patch

import pytest

from fast_db.dependency import DBDependency


def test_db_dependency_raises_when_no_session():
    with patch("fast_db.dependency.get_db_session", return_value=None):
        with pytest.raises(RuntimeError, match="not initialized"):
            DBDependency.derive()


def test_db_dependency_returns_session():
    mock_s = MagicMock()
    with patch("fast_db.dependency.get_db_session", return_value=mock_s):
        assert DBDependency.derive() is mock_s
