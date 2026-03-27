"""AWS Secrets Manager backend."""

from __future__ import annotations

from typing import Any, Optional

from .base import ISecretsBackend


class AwsSecretsBackend(ISecretsBackend):
    """AWS Secrets Manager backend."""

    name = "aws"

    def __init__(
        self,
        region: str = "us-east-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        prefix: str = "",
    ) -> None:
        """Execute __init__ operation.

        Args:
            region: The region parameter.
            access_key_id: The access_key_id parameter.
            secret_access_key: The secret_access_key parameter.
            prefix: The prefix parameter.
        """
        try:
            import boto3
        except ImportError as e:
            raise RuntimeError(
                "boto3 is required for AWS Secrets. Install: pip install fast_secrets[aws]"
            ) from e
        kwargs = {"region_name": region}
        if access_key_id and secret_access_key:
            kwargs["aws_access_key_id"] = access_key_id
            kwargs["aws_secret_access_key"] = secret_access_key
        self._client = boto3.client("secretsmanager", **kwargs)
        self._prefix = prefix.rstrip("/")

    def _secret_id(self, key: str) -> str:
        """Execute _secret_id operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        return f"{self._prefix}/{key}".strip("/") if self._prefix else key

    def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
        """Execute get_secret operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        try:
            r = self._client.get_secret_value(SecretId=self._secret_id(key))
            return r.get("SecretString")
        except Exception:
            return None

    def set_secret(self, key: str, value: str) -> None:
        """Execute set_secret operation.

        Args:
            key: The key parameter.
            value: The value parameter.

        Returns:
            The result of the operation.
        """
        try:
            self._client.create_secret(Name=self._secret_id(key), SecretString=value)
        except self._client.exceptions.ResourceExistsException:
            self._client.put_secret_value(SecretId=self._secret_id(key), SecretString=value)
