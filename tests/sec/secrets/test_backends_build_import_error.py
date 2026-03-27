"""Module test_backends_build_import_error.py."""

from __future__ import annotations

"""Tests for :func:`sec.secrets.base.build_secrets_backend` when backend modules fail to import."""
import builtins
import sys
import types

import pytest

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsBuildImportError(ISecretsTests):
    """Represents the TestBackendsBuildImportError class."""

    def test_build_secrets_backend_import_error_returns_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Execute test_build_secrets_backend_import_error_returns_none operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        from sec.secrets import base as secrets_base

        class FakeCfg:
            """Represents the FakeCfg class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.vault = types.SimpleNamespace(
                    enabled=True, url="http://vault", token="t", mount_point=None
                )
                self.aws = types.SimpleNamespace(
                    enabled=True,
                    region="us-east-1",
                    access_key_id=None,
                    secret_access_key=None,
                    prefix="p",
                )
                self.gcp = types.SimpleNamespace(
                    enabled=True, project_id="pid", credentials_json_path=None
                )

        monkeypatch.setattr(
            secrets_base,
            "SecretsConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        real_import = builtins.__import__

        def _fail_backend_import(name: str, *args: object, **kwargs: object):
            """Execute _fail_backend_import operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
            if "vault_backend" in name or "aws_backend" in name or "gcp_backend" in name:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fail_backend_import)
        sys.modules.pop("sec.secrets.vault_backend", None)
        sys.modules.pop("sec.secrets.aws_backend", None)
        sys.modules.pop("sec.secrets.gcp_backend", None)
        assert secrets_base.build_secrets_backend("vault") is None
        assert secrets_base.build_secrets_backend("aws") is None
        assert secrets_base.build_secrets_backend("gcp") is None
