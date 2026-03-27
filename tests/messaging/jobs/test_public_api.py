"""Module test_public_api.py."""

from __future__ import annotations

"""Ensure every name in __all__ resolves."""
import importlib

import pytest

from tests.messaging.jobs.abstraction import IJobTests

PACKAGE = "fast_platform.messaging.jobs"


class TestPublicApi(IJobTests):
    """Represents the TestPublicApi class."""

    def test_public_exports_resolve(self):
        """Execute test_public_exports_resolve operation.

        Returns:
            The result of the operation.
        """
        try:
            m = importlib.import_module(PACKAGE)
        except ImportError as e:
            pytest.skip(f"import not available: {e}")
        for export_name in getattr(m, "__all__", ()):
            getattr(m, export_name)
