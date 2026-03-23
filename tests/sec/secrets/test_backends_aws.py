from __future__ import annotations

"""Tests for :class:`sec.secrets.aws_backend.AwsSecretsBackend`."""
import sys
import types

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsAws(ISecretsTests):
    def test_aws_secrets_backend_get_secret_and_set_secret_happy_and_exists(self) -> None:
        from sec.secrets.aws_backend import AwsSecretsBackend

        class FakeResourceExistsException(Exception):
            pass

        class FakeSecretsManagerClient:
            def __init__(self) -> None:
                self.created: list[tuple[str, str]] = []
                self.puts: list[tuple[str, str]] = []
                self.exceptions = types.SimpleNamespace(
                    ResourceExistsException=FakeResourceExistsException
                )

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
        fake_boto3.client = lambda service_name, **kwargs: FakeSecretsManagerClient()
        sys.modules["boto3"] = fake_boto3
        backend = AwsSecretsBackend(
            region="us-east-1", access_key_id=None, secret_access_key=None, prefix="p"
        )
        assert backend.get_secret("key") == "s3cr3t"
        backend.set_secret("new", "v1")
        backend.set_secret("exists", "v2")
        assert backend._client.created == [("p/new", "v1")]
        assert backend._client.puts == [("p/exists", "v2")]

    def test_aws_secrets_backend_get_secret_exception_returns_none(self) -> None:
        from sec.secrets.aws_backend import AwsSecretsBackend

        class FakeSecretsManagerClient:
            def __init__(self) -> None:
                self.exceptions = types.SimpleNamespace(ResourceExistsException=Exception)

            def get_secret_value(self, *, SecretId: str):
                raise RuntimeError("fail")

            def create_secret(self, *, Name: str, SecretString: str):
                pass

            def put_secret_value(self, *, SecretId: str, SecretString: str):
                pass

        fake_boto3 = types.ModuleType("boto3")
        fake_boto3.client = lambda service_name, **kwargs: FakeSecretsManagerClient()
        sys.modules["boto3"] = fake_boto3
        backend = AwsSecretsBackend(prefix="")
        assert backend.get_secret("any") is None
