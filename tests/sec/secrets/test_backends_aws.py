"""Module test_backends_aws.py."""

from __future__ import annotations

"""Tests for :class:`sec.secrets.aws_backend.AwsSecretsBackend`."""
import sys
import types

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsAws(ISecretsTests):
    """Represents the TestBackendsAws class."""

    def test_aws_secrets_backend_get_secret_and_set_secret_happy_and_exists(self) -> None:
        """Execute test_aws_secrets_backend_get_secret_and_set_secret_happy_and_exists operation.

        Returns:
            The result of the operation.
        """
        from sec.secrets.aws_backend import AwsSecretsBackend

        class FakeResourceExistsException(Exception):
            """Represents the FakeResourceExistsException class."""

            pass

        class FakeSecretsManagerClient:
            """Represents the FakeSecretsManagerClient class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.created: list[tuple[str, str]] = []
                self.puts: list[tuple[str, str]] = []
                self.exceptions = types.SimpleNamespace(
                    ResourceExistsException=FakeResourceExistsException
                )

            def get_secret_value(self, *, SecretId: str):
                """Execute get_secret_value operation.

                Args:
                    SecretId: The SecretId parameter.

                Returns:
                    The result of the operation.
                """
                assert SecretId == "p/key"
                return {"SecretString": "s3cr3t"}

            def create_secret(self, *, Name: str, SecretString: str):
                """Execute create_secret operation.

                Args:
                    Name: The Name parameter.
                    SecretString: The SecretString parameter.

                Returns:
                    The result of the operation.
                """
                if Name == "p/exists":
                    raise FakeResourceExistsException()
                self.created.append((Name, SecretString))

            def put_secret_value(self, *, SecretId: str, SecretString: str):
                """Execute put_secret_value operation.

                Args:
                    SecretId: The SecretId parameter.
                    SecretString: The SecretString parameter.

                Returns:
                    The result of the operation.
                """
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
        """Execute test_aws_secrets_backend_get_secret_exception_returns_none operation.

        Returns:
            The result of the operation.
        """
        from sec.secrets.aws_backend import AwsSecretsBackend

        class FakeSecretsManagerClient:
            """Represents the FakeSecretsManagerClient class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.exceptions = types.SimpleNamespace(ResourceExistsException=Exception)

            def get_secret_value(self, *, SecretId: str):
                """Execute get_secret_value operation.

                Args:
                    SecretId: The SecretId parameter.

                Returns:
                    The result of the operation.
                """
                raise RuntimeError("fail")

            def create_secret(self, *, Name: str, SecretString: str):
                """Execute create_secret operation.

                Args:
                    Name: The Name parameter.
                    SecretString: The SecretString parameter.

                Returns:
                    The result of the operation.
                """
                pass

            def put_secret_value(self, *, SecretId: str, SecretString: str):
                """Execute put_secret_value operation.

                Args:
                    SecretId: The SecretId parameter.
                    SecretString: The SecretString parameter.

                Returns:
                    The result of the operation.
                """
                pass

        fake_boto3 = types.ModuleType("boto3")
        fake_boto3.client = lambda service_name, **kwargs: FakeSecretsManagerClient()
        sys.modules["boto3"] = fake_boto3
        backend = AwsSecretsBackend(prefix="")
        assert backend.get_secret("any") is None
