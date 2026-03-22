from __future__ import annotations

"""Tests for :class:`secrets.gcp_backend.GcpSecretsBackend`."""
import sys
import types
from typing import Any

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsGcp(ISecretsTests):
    def test_gcp_secrets_backend_get_secret_and_set_secret(self) -> None:
        from secrets.gcp_backend import GcpSecretsBackend

        class FakePayload:
            def __init__(self, data: bytes) -> None:
                self.data = data

        class FakeSecretManagerClient:
            def __init__(self) -> None:
                self.created: list[dict[str, Any]] = []
                self.added: list[dict[str, Any]] = []

            def access_secret_version(self, *, name: str):
                assert "projects/pid/secrets/mykey/versions/latest" in name
                return types.SimpleNamespace(payload=FakePayload(b"decoded"))

            def create_secret(self, request: dict[str, Any]):
                raise RuntimeError("exists")

            def add_secret_version(self, request: dict[str, Any]):
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
        from secrets.gcp_backend import GcpSecretsBackend

        class FakeSecretManagerClient:
            def access_secret_version(self, *, name: str):
                raise RuntimeError("boom")

            def create_secret(self, request: dict[str, Any]):
                pass

            def add_secret_version(self, request: dict[str, Any]):
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
