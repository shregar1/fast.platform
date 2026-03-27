"""Module test_backends_build_disabled.py."""

from __future__ import annotations

"""Tests for :func:`sec.secrets.base.build_secrets_backend` when providers are disabled."""
import types

import pytest

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsBuildDisabled(ISecretsTests):
    """Represents the TestBackendsBuildDisabled class."""

    def test_build_secrets_backend_returns_none_when_disabled(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Execute test_build_secrets_backend_returns_none_when_disabled operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        from fast_platform.sec.secrets import base as secrets_base

        class FakeCfg:
            """Represents the FakeCfg class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.vault = types.SimpleNamespace(
                    enabled=False, url=None, token=None, mount_point=None
                )
                self.aws = types.SimpleNamespace(enabled=False)
                self.gcp = types.SimpleNamespace(enabled=False)

        monkeypatch.setattr(
            secrets_base,
            "SecretsConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        assert secrets_base.build_secrets_backend("vault") is None
        assert secrets_base.build_secrets_backend("aws") is None
        assert secrets_base.build_secrets_backend("gcp") is None
