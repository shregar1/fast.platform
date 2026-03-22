"""DBDependency."""

from unittest.mock import MagicMock, patch

import pytest

from db.dependency import DBDependency
from tests.persistence.db.abstraction import IDatabaseTests


class TestDependency(IDatabaseTests):
    def test_db_dependency_raises_when_no_session(self):
        with patch("db.dependency.get_db_session", return_value=None):
            with pytest.raises(RuntimeError, match="not initialized"):
                DBDependency.derive()

    def test_db_dependency_returns_session(self):
        mock_s = MagicMock()
        with patch("db.dependency.get_db_session", return_value=mock_s):
            assert DBDependency.derive() is mock_s
