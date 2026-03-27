"""DBDependency."""

from unittest.mock import MagicMock, patch

import pytest

from fast_platform.persistence.db.dependency import DBDependency
from tests.persistence.db.abstraction import IDatabaseTests


class TestDependency(IDatabaseTests):
    """Represents the TestDependency class."""

    def test_db_dependency_raises_when_no_session(self):
        """Execute test_db_dependency_raises_when_no_session operation.

        Returns:
            The result of the operation.
        """
        with patch("fast_platform.persistence.db.dependency.get_db_session", return_value=None):
            with pytest.raises(RuntimeError, match="not initialized"):
                DBDependency.derive()

    def test_db_dependency_returns_session(self):
        """Execute test_db_dependency_returns_session operation.

        Returns:
            The result of the operation.
        """
        mock_s = MagicMock()
        with patch("fast_platform.persistence.db.dependency.get_db_session", return_value=mock_s):
            assert DBDependency.derive() is mock_s
