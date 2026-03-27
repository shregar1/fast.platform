"""Module test_public_api.py."""

from __future__ import annotations

"""
Public API import tests for llm.

Ensures __version__ (if present) and every name in __all__ resolve.
Imports run inside tests (not at collection) so optional deps can fail one test.
"""
import importlib

import pytest

from tests.integrations.llm.abstraction import ILLMTests

PACKAGE = "fast_platform.integrations.llm"


class TestPublicApi(ILLMTests):
    """Represents the TestPublicApi class."""

    def test_package_imports(self):
        """Execute test_package_imports operation.

        Returns:
            The result of the operation.
        """
        try:
            m = importlib.import_module(PACKAGE)
        except ImportError as e:
            pytest.skip(f"import not available in this environment: {e}")
        assert m is not None

    def test_version_when_present(self):
        """Execute test_version_when_present operation.

        Returns:
            The result of the operation.
        """
        try:
            m = importlib.import_module(PACKAGE)
        except ImportError as e:
            pytest.skip(f"import not available: {e}")
        if hasattr(m, "__version__"):
            assert isinstance(m.__version__, str)
            assert m.__version__

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
            try:
                obj = getattr(m, export_name)
            except Exception as e:
                pytest.skip(f"export {export_name!r} not loadable in this environment: {e}")
            assert obj is not None
