"""Module test_init.py."""

from __future__ import annotations

"""Smoke tests for ``secrets`` package exports."""
from tests.sec.secrets.abstraction import ISecretsTests


class TestInit(ISecretsTests):
    """Represents the TestInit class."""

    def test_imports(self) -> None:
        """Execute test_imports operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.sec.secrets import (
            CachedSecretsBackend,
            LeasedSecretsBackend,
            RotationCallback,
            build_secrets_backend,
            redact_text,
        )

        assert build_secrets_backend is not None
        assert CachedSecretsBackend is not None
        assert LeasedSecretsBackend is not None
        assert RotationCallback is not None
        assert redact_text("x", "x") == "***"
        import fast_platform.sec.secrets as sec_pkg

        assert sec_pkg.__version__ == "0.3.0"
