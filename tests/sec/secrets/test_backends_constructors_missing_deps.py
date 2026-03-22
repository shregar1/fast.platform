from __future__ import annotations
"""Tests for backend constructors when optional dependencies are missing."""
from tests.sec.secrets.abstraction import ISecretsTests



import builtins

import pytest


class TestBackendsConstructorsMissingDeps(ISecretsTests):
    def test_provider_backend_constructors_raise_runtime_error_when_dependency_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from secrets.aws_backend import AwsSecretsBackend
        from secrets.gcp_backend import GcpSecretsBackend
        from secrets.vault_backend import VaultSecretsBackend

        real_import = builtins.__import__

        def _deny_import(name: str, *args: object, **kwargs: object):
            if name in {"boto3", "google.cloud", "hvac", "google"}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _deny_import)
        with pytest.raises(RuntimeError):
            AwsSecretsBackend()
        with pytest.raises(RuntimeError):
            GcpSecretsBackend(project_id="pid")
        with pytest.raises(RuntimeError):
            VaultSecretsBackend(url="http://vault")
