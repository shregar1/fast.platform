"""Module test_backends_constructors_missing_deps.py."""

from __future__ import annotations

"""Tests for backend constructors when optional dependencies are missing."""
import builtins

import pytest

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsConstructorsMissingDeps(ISecretsTests):
    """Represents the TestBackendsConstructorsMissingDeps class."""

    def test_provider_backend_constructors_raise_runtime_error_when_dependency_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Execute test_provider_backend_constructors_raise_runtime_error_when_dependency_missing operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """
        from sec.secrets.aws_backend import AwsSecretsBackend
        from sec.secrets.gcp_backend import GcpSecretsBackend
        from sec.secrets.vault_backend import VaultSecretsBackend

        real_import = builtins.__import__

        def _deny_import(name: str, *args: object, **kwargs: object):
            """Execute _deny_import operation.

            Args:
                name: The name parameter.

            Returns:
                The result of the operation.
            """
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
