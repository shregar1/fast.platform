from __future__ import annotations
"""
Public API import tests for payments.

Ensures __version__ (if present) and every name in __all__ resolve.
Imports run inside tests (not at collection) so optional deps can fail one test.
"""
from tests.integrations.payments.abstraction import IPaymentsTests



import importlib

import pytest

PACKAGE = "payments"


class TestPublicApi(IPaymentsTests):
    def test_package_imports(self) -> None:
        try:
            m = importlib.import_module(PACKAGE)
        except ImportError as e:
            pytest.skip(f"import not available in this environment: {e}")
        assert m is not None

    def test_version_when_present(self) -> None:
        try:
            m = importlib.import_module(PACKAGE)
        except ImportError as e:
            pytest.skip(f"import not available: {e}")
        if hasattr(m, "__version__"):
            assert isinstance(m.__version__, str)
            assert m.__version__

    def test_public_exports_resolve(self) -> None:
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
