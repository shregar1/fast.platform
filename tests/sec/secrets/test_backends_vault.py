"""Module test_backends_vault.py."""

from __future__ import annotations

"""Tests for Vault-backed :func:`sec.secrets.base.build_secrets_backend` and :class:`sec.secrets.vault_backend.VaultSecretsBackend`."""
import sys
import types
from typing import Any, Optional

import pytest

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsVault(ISecretsTests):
    """Represents the TestBackendsVault class."""

    def test_build_secrets_backend_selects_vault_and_calls_methods(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Execute test_build_secrets_backend_selects_vault_and_calls_methods operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        from sec.secrets import base as secrets_base
        from sec.secrets.vault_backend import VaultSecretsBackend

        class FakeKVv2:
            """Represents the FakeKVv2 class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.created: list[dict[str, Any]] = []

            def read_secret_version(self, *, path: str, mount_point: str):
                """Execute read_secret_version operation.

                Args:
                    path: The path parameter.
                    mount_point: The mount_point parameter.

                Returns:
                    The result of the operation.
                """
                assert mount_point == "secret"
                if path == "foo/bar":
                    return {"data": {"data": {"value": "abc"}}}
                return {"data": {"data": {}}}

            def create_or_update_secret(
                self, *, path: str, secret: dict[str, Any], mount_point: str
            ):
                """Execute create_or_update_secret operation.

                Args:
                    path: The path parameter.
                    secret: The secret parameter.
                    mount_point: The mount_point parameter.

                Returns:
                    The result of the operation.
                """
                self.created.append({"path": path, "secret": secret, "mount_point": mount_point})

        class FakeSecrets:
            """Represents the FakeSecrets class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.kv = types.SimpleNamespace(v2=FakeKVv2())

        class FakeHVACClient:
            """Represents the FakeHVACClient class."""

            def __init__(self, url: str, token: Optional[str]):
                """Execute __init__ operation.

                Args:
                    url: The url parameter.
                    token: The token parameter.
                """
                self.url = url
                self.token = token
                self.secrets = FakeSecrets()

        fake_hvac = types.ModuleType("hvac")
        fake_hvac.Client = FakeHVACClient
        sys.modules["hvac"] = fake_hvac

        class FakeCfg:
            """Represents the FakeCfg class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.vault = types.SimpleNamespace(
                    enabled=True, url="http://vault", token="t", mount_point=None
                )
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

    def test_vault_backend_get_secret_exception_returns_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Execute test_vault_backend_get_secret_exception_returns_none operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        from sec.secrets.vault_backend import VaultSecretsBackend

        class FakeKVv2:
            """Represents the FakeKVv2 class."""

            def read_secret_version(self, *, path: str, mount_point: str):
                """Execute read_secret_version operation.

                Args:
                    path: The path parameter.
                    mount_point: The mount_point parameter.

                Returns:
                    The result of the operation.
                """
                raise RuntimeError("boom")

            def create_or_update_secret(
                self, *, path: str, secret: dict[str, Any], mount_point: str
            ):
                """Execute create_or_update_secret operation.

                Args:
                    path: The path parameter.
                    secret: The secret parameter.
                    mount_point: The mount_point parameter.

                Returns:
                    The result of the operation.
                """
                pass

        class FakeSecrets:
            """Represents the FakeSecrets class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.kv = types.SimpleNamespace(v2=FakeKVv2())

        class FakeHVACClient:
            """Represents the FakeHVACClient class."""

            def __init__(self, url: str, token: Optional[str]):
                """Execute __init__ operation.

                Args:
                    url: The url parameter.
                    token: The token parameter.
                """
                self.secrets = FakeSecrets()

        fake_hvac = types.ModuleType("hvac")
        fake_hvac.Client = FakeHVACClient
        sys.modules["hvac"] = fake_hvac
        backend = VaultSecretsBackend(url="http://vault", token=None, mount_point="secret")
        assert backend.get_secret("any") is None
