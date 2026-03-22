from __future__ import annotations
"""Tests for Vault-backed :func:`secrets.base.build_secrets_backend` and :class:`secrets.vault_backend.VaultSecretsBackend`."""
from tests.sec.secrets.abstraction import ISecretsTests



import sys
import types
from typing import Any, Optional

import pytest


class TestBackendsVault(ISecretsTests):
    def test_build_secrets_backend_selects_vault_and_calls_methods(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from secrets import base as secrets_base
        from secrets.vault_backend import VaultSecretsBackend

        class FakeKVv2:
            def __init__(self) -> None:
                self.created: list[dict[str, Any]] = []

            def read_secret_version(self, *, path: str, mount_point: str):
                assert mount_point == "secret"
                if path == "foo/bar":
                    return {"data": {"data": {"value": "abc"}}}
                return {"data": {"data": {}}}

            def create_or_update_secret(self, *, path: str, secret: dict[str, Any], mount_point: str):
                self.created.append({"path": path, "secret": secret, "mount_point": mount_point})

        class FakeSecrets:
            def __init__(self) -> None:
                self.kv = types.SimpleNamespace(v2=FakeKVv2())

        class FakeHVACClient:
            def __init__(self, url: str, token: Optional[str]):
                self.url = url
                self.token = token
                self.secrets = FakeSecrets()

        fake_hvac = types.ModuleType("hvac")
        fake_hvac.Client = FakeHVACClient
        sys.modules["hvac"] = fake_hvac

        class FakeCfg:
            def __init__(self) -> None:
                self.vault = types.SimpleNamespace(enabled=True, url="http://vault", token="t", mount_point=None)
                self.aws = types.SimpleNamespace(enabled=False)
                self.gcp = types.SimpleNamespace(enabled=False)

        monkeypatch.setattr(
            secrets_base,
            "SecretsConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        backend = secrets_base.build_secrets_backend("vault")
        assert isinstance(backend, VaultSecretsBackend)
        assert backend.get_secret("foo/bar") == "abc"
        assert backend.get_secret("missing") is None
        backend.set_secret("foo/baz", "val")
        kv = backend._client.secrets.kv.v2
        assert kv.created[-1]["path"] == "foo/baz"
        assert kv.created[-1]["secret"]["value"] == "val"

    def test_vault_backend_get_secret_exception_returns_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from secrets.vault_backend import VaultSecretsBackend

        class FakeKVv2:
            def read_secret_version(self, *, path: str, mount_point: str):
                raise RuntimeError("boom")

            def create_or_update_secret(self, *, path: str, secret: dict[str, Any], mount_point: str):
                pass

        class FakeSecrets:
            def __init__(self) -> None:
                self.kv = types.SimpleNamespace(v2=FakeKVv2())

        class FakeHVACClient:
            def __init__(self, url: str, token: Optional[str]):
                self.secrets = FakeSecrets()

        fake_hvac = types.ModuleType("hvac")
        fake_hvac.Client = FakeHVACClient
        sys.modules["hvac"] = fake_hvac
        backend = VaultSecretsBackend(url="http://vault", token=None, mount_point="secret")
        assert backend.get_secret("any") is None
