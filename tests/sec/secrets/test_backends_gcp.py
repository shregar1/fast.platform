"""Module test_backends_gcp.py."""

from __future__ import annotations

"""Tests for :class:`sec.secrets.gcp_backend.GcpSecretsBackend`."""
import sys
import types
from typing import Any

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsGcp(ISecretsTests):
    """Represents the TestBackendsGcp class."""

    def test_gcp_secrets_backend_get_secret_and_set_secret(self) -> None:
        """Execute test_gcp_secrets_backend_get_secret_and_set_secret operation.

        Returns:
            The result of the operation.
        """
        from sec.secrets.gcp_backend import GcpSecretsBackend

        class FakePayload:
            """Represents the FakePayload class."""

            def __init__(self, data: bytes) -> None:
                """Execute __init__ operation.

                Args:
                    data: The data parameter.
                """
                self.data = data

        class FakeSecretManagerClient:
            """Represents the FakeSecretManagerClient class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.created: list[dict[str, Any]] = []
                self.added: list[dict[str, Any]] = []

            def access_secret_version(self, *, name: str):
                """Execute access_secret_version operation.

                Args:
                    name: The name parameter.

                Returns:
                    The result of the operation.
                """
                assert "projects/pid/secrets/mykey/versions/latest" in name
                return types.SimpleNamespace(payload=FakePayload(b"decoded"))

            def create_secret(self, request: dict[str, Any]):
                """Execute create_secret operation.

                Args:
                    request: The request parameter.

                Returns:
                    The result of the operation.
                """
                raise RuntimeError("exists")

            def add_secret_version(self, request: dict[str, Any]):
                """Execute add_secret_version operation.

                Args:
                    request: The request parameter.

                Returns:
                    The result of the operation.
                """
                self.added.append(request)

        fake_secretmanager = types.ModuleType("secretmanager")
        fake_secretmanager.SecretManagerServiceClient = FakeSecretManagerClient
        fake_google = types.ModuleType("google")
        fake_google_cloud = types.ModuleType("google.cloud")
        fake_google_cloud.secretmanager = fake_secretmanager
        sys.modules["google"] = fake_google
        sys.modules["google.cloud"] = fake_google_cloud
        sys.modules["google.cloud.secretmanager"] = fake_secretmanager
        backend = GcpSecretsBackend(project_id="pid", credentials_path=None)
        assert backend.get_secret("mykey") == "decoded"
        backend.set_secret("mykey", "value1")
        assert backend._client.added[-1]["parent"].endswith("/secrets/mykey")

    def test_gcp_secrets_backend_get_secret_exception_returns_none(self) -> None:
        """Execute test_gcp_secrets_backend_get_secret_exception_returns_none operation.

        Returns:
            The result of the operation.
        """
        from sec.secrets.gcp_backend import GcpSecretsBackend

        class FakeSecretManagerClient:
            """Represents the FakeSecretManagerClient class."""

            def access_secret_version(self, *, name: str):
                """Execute access_secret_version operation.

                Args:
                    name: The name parameter.

                Returns:
                    The result of the operation.
                """
                raise RuntimeError("boom")

            def create_secret(self, request: dict[str, Any]):
                """Execute create_secret operation.

                Args:
                    request: The request parameter.

                Returns:
                    The result of the operation.
                """
                pass

            def add_secret_version(self, request: dict[str, Any]):
                """Execute add_secret_version operation.

                Args:
                    request: The request parameter.

                Returns:
                    The result of the operation.
                """
                pass

        fake_secretmanager = types.ModuleType("secretmanager")
        fake_secretmanager.SecretManagerServiceClient = FakeSecretManagerClient
        fake_google = types.ModuleType("google")
        fake_google_cloud = types.ModuleType("google.cloud")
        fake_google_cloud.secretmanager = fake_secretmanager
        sys.modules["google"] = fake_google
        sys.modules["google.cloud"] = fake_google_cloud
        sys.modules["google.cloud.secretmanager"] = fake_secretmanager
        backend = GcpSecretsBackend(project_id="pid", credentials_path=None)
        assert backend.get_secret("any") is None
