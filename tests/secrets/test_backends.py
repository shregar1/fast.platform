import builtins
import sys
import types
from typing import Any, Optional

import pytest


def test_is_secrets_backend_abstract_methods_raise_not_implemented():
    from fast_secrets.base import ISecretsBackend

    class DummyBackend(ISecretsBackend):
        name = "dummy"

        def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
            return super().get_secret(key, **kwargs)

        def set_secret(self, key: str, value: str) -> None:
            return super().set_secret(key, value)

    b = DummyBackend()
    with pytest.raises(NotImplementedError):
        b.get_secret("k")
    with pytest.raises(NotImplementedError):
        b.set_secret("k", "v")


def test_build_secrets_backend_selects_vault_and_calls_methods(monkeypatch):
    from fast_secrets import base as secrets_base
    from fast_secrets.vault_backend import VaultSecretsBackend

    # Fake hvac client.
    class FakeKVv2:
        def __init__(self):
            self.created: list[dict[str, Any]] = []

        def read_secret_version(self, *, path: str, mount_point: str):
            assert mount_point == "secret"
            if path == "foo/bar":
                return {"data": {"data": {"value": "abc"}}}
            return {"data": {"data": {}}}

        def create_or_update_secret(self, *, path: str, secret: dict[str, Any], mount_point: str):
            self.created.append({"path": path, "secret": secret, "mount_point": mount_point})

    class FakeSecrets:
        def __init__(self):
            self.kv = types.SimpleNamespace(v2=FakeKVv2())

    class FakeHVACClient:
        def __init__(self, url: str, token: Optional[str]):
            self.url = url
            self.token = token
            self.secrets = FakeSecrets()

    fake_hvac = types.ModuleType("hvac")
    fake_hvac.Client = FakeHVACClient  # type: ignore[attr-defined]
    sys.modules["hvac"] = fake_hvac

    class FakeCfg:
        def __init__(self):
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

    # Touch internal fake for verification.
    kv = backend._client.secrets.kv.v2  # type: ignore[attr-defined]
    assert kv.created[-1]["path"] == "foo/baz"
    assert kv.created[-1]["secret"]["value"] == "val"


def test_vault_backend_get_secret_exception_returns_none(monkeypatch):
    from fast_secrets.vault_backend import VaultSecretsBackend

    class FakeKVv2:
        def read_secret_version(self, *, path: str, mount_point: str):
            raise RuntimeError("boom")

        def create_or_update_secret(self, *, path: str, secret: dict[str, Any], mount_point: str):
            pass

    class FakeSecrets:
        def __init__(self):
            self.kv = types.SimpleNamespace(v2=FakeKVv2())

    class FakeHVACClient:
        def __init__(self, url: str, token: Optional[str]):
            self.secrets = FakeSecrets()

    fake_hvac = types.ModuleType("hvac")
    fake_hvac.Client = FakeHVACClient  # type: ignore[attr-defined]
    sys.modules["hvac"] = fake_hvac

    backend = VaultSecretsBackend(url="http://vault", token=None, mount_point="secret")
    assert backend.get_secret("any") is None


def test_build_secrets_backend_returns_none_when_disabled(monkeypatch):
    from fast_secrets import base as secrets_base

    class FakeCfg:
        def __init__(self):
            self.vault = types.SimpleNamespace(enabled=False, url=None, token=None, mount_point=None)
            self.aws = types.SimpleNamespace(enabled=False)
            self.gcp = types.SimpleNamespace(enabled=False)

    monkeypatch.setattr(secrets_base, "SecretsConfiguration", lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()), raising=True)
    assert secrets_base.build_secrets_backend("vault") is None
    assert secrets_base.build_secrets_backend("aws") is None
    assert secrets_base.build_secrets_backend("gcp") is None


def test_build_secrets_backend_import_error_returns_none(monkeypatch):
    from fast_secrets import base as secrets_base

    class FakeCfg:
        def __init__(self):
            self.vault = types.SimpleNamespace(enabled=True, url="http://vault", token="t", mount_point=None)
            self.aws = types.SimpleNamespace(enabled=True, region="us-east-1", access_key_id=None, secret_access_key=None, prefix="p")
            self.gcp = types.SimpleNamespace(enabled=True, project_id="pid", credentials_json_path=None)

    monkeypatch.setattr(secrets_base, "SecretsConfiguration", lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()), raising=True)

    real_import = builtins.__import__

    def _fail_backend_import(name, *args, **kwargs):
        if "vault_backend" in name or "aws_backend" in name or "gcp_backend" in name:
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fail_backend_import)

    # Ensure backend modules are forced to re-import.
    sys.modules.pop("fast_secrets.vault_backend", None)
    sys.modules.pop("fast_secrets.aws_backend", None)
    sys.modules.pop("fast_secrets.gcp_backend", None)

    assert secrets_base.build_secrets_backend("vault") is None
    assert secrets_base.build_secrets_backend("aws") is None
    assert secrets_base.build_secrets_backend("gcp") is None


def test_aws_secrets_backend_get_secret_and_set_secret_happy_and_exists(monkeypatch):
    from fast_secrets.aws_backend import AwsSecretsBackend

    class FakeResourceExistsException(Exception):
        pass

    class FakeSecretsManagerClient:
        def __init__(self):
            self.created: list[tuple[str, str]] = []
            self.puts: list[tuple[str, str]] = []
            self.exceptions = types.SimpleNamespace(ResourceExistsException=FakeResourceExistsException)

        def get_secret_value(self, *, SecretId: str):
            assert SecretId == "p/key"
            return {"SecretString": "s3cr3t"}

        def create_secret(self, *, Name: str, SecretString: str):
            if Name == "p/exists":
                raise FakeResourceExistsException()
            self.created.append((Name, SecretString))

        def put_secret_value(self, *, SecretId: str, SecretString: str):
            self.puts.append((SecretId, SecretString))

    fake_boto3 = types.ModuleType("boto3")
    fake_boto3.client = lambda service_name, **kwargs: FakeSecretsManagerClient()  # type: ignore[assignment]
    sys.modules["boto3"] = fake_boto3

    backend = AwsSecretsBackend(region="us-east-1", access_key_id=None, secret_access_key=None, prefix="p")
    assert backend.get_secret("key") == "s3cr3t"

    backend.set_secret("new", "v1")
    backend.set_secret("exists", "v2")

    assert backend._client.created == [("p/new", "v1")]  # type: ignore[attr-defined]
    assert backend._client.puts == [("p/exists", "v2")]  # type: ignore[attr-defined]


def test_aws_secrets_backend_get_secret_exception_returns_none():
    from fast_secrets.aws_backend import AwsSecretsBackend

    class FakeSecretsManagerClient:
        def __init__(self):
            self.exceptions = types.SimpleNamespace(ResourceExistsException=Exception)

        def get_secret_value(self, *, SecretId: str):
            raise RuntimeError("fail")

        def create_secret(self, *, Name: str, SecretString: str):
            pass

        def put_secret_value(self, *, SecretId: str, SecretString: str):
            pass

    fake_boto3 = types.ModuleType("boto3")
    fake_boto3.client = lambda service_name, **kwargs: FakeSecretsManagerClient()  # type: ignore[assignment]
    sys.modules["boto3"] = fake_boto3

    backend = AwsSecretsBackend(prefix="")
    assert backend.get_secret("any") is None


def test_gcp_secrets_backend_get_secret_and_set_secret():
    from fast_secrets.gcp_backend import GcpSecretsBackend

    class FakePayload:
        def __init__(self, data: bytes):
            self.data = data

    class FakeSecretManagerClient:
        def __init__(self):
            self.created: list[dict[str, Any]] = []
            self.added: list[dict[str, Any]] = []

        def access_secret_version(self, *, name: str):
            assert "projects/pid/secrets/mykey/versions/latest" in name
            return types.SimpleNamespace(payload=FakePayload(b"decoded"))

        def create_secret(self, request: dict[str, Any]):
            # Simulate secret already exists (create raises)
            raise RuntimeError("exists")

        def add_secret_version(self, request: dict[str, Any]):
            self.added.append(request)

    fake_secretmanager = types.ModuleType("secretmanager")
    fake_secretmanager.SecretManagerServiceClient = FakeSecretManagerClient  # type: ignore[attr-defined]

    # Build package structure google.cloud.secretmanager
    fake_google = types.ModuleType("google")
    fake_google_cloud = types.ModuleType("google.cloud")
    fake_google_cloud.secretmanager = fake_secretmanager  # type: ignore[attr-defined]

    sys.modules["google"] = fake_google
    sys.modules["google.cloud"] = fake_google_cloud
    sys.modules["google.cloud.secretmanager"] = fake_secretmanager

    backend = GcpSecretsBackend(project_id="pid", credentials_path=None)
    assert backend.get_secret("mykey") == "decoded"
    backend.set_secret("mykey", "value1")

    assert backend._client.added[-1]["parent"].endswith("/secrets/mykey")  # type: ignore[attr-defined]


def test_gcp_secrets_backend_get_secret_exception_returns_none():
    from fast_secrets.gcp_backend import GcpSecretsBackend

    class FakeSecretManagerClient:
        def access_secret_version(self, *, name: str):
            raise RuntimeError("boom")

        def create_secret(self, request: dict[str, Any]):
            pass

        def add_secret_version(self, request: dict[str, Any]):
            pass

    fake_secretmanager = types.ModuleType("secretmanager")
    fake_secretmanager.SecretManagerServiceClient = FakeSecretManagerClient  # type: ignore[attr-defined]

    fake_google = types.ModuleType("google")
    fake_google_cloud = types.ModuleType("google.cloud")
    fake_google_cloud.secretmanager = fake_secretmanager  # type: ignore[attr-defined]

    sys.modules["google"] = fake_google
    sys.modules["google.cloud"] = fake_google_cloud
    sys.modules["google.cloud.secretmanager"] = fake_secretmanager

    backend = GcpSecretsBackend(project_id="pid", credentials_path=None)
    assert backend.get_secret("any") is None


def test_provider_backend_constructors_raise_runtime_error_when_dependency_missing(monkeypatch):
    from fast_secrets.aws_backend import AwsSecretsBackend
    from fast_secrets.gcp_backend import GcpSecretsBackend
    from fast_secrets.vault_backend import VaultSecretsBackend

    real_import = builtins.__import__

    def _deny_import(name, *args, **kwargs):
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

