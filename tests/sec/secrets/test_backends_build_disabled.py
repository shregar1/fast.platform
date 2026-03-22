from __future__ import annotations
"""Tests for :func:`secrets.base.build_secrets_backend` when providers are disabled."""
from tests.sec.secrets.abstraction import ISecretsTests



import types

import pytest


class TestBackendsBuildDisabled(ISecretsTests):
    def test_build_secrets_backend_returns_none_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from secrets import base as secrets_base

        class FakeCfg:
            def __init__(self) -> None:
                self.vault = types.SimpleNamespace(enabled=False, url=None, token=None, mount_point=None)
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
