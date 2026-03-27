"""GCP Secret Manager backend."""

from __future__ import annotations

from typing import Any, Optional

from .base import ISecretsBackend


class GcpSecretsBackend(ISecretsBackend):
    """Google Cloud Secret Manager backend."""

    name = "gcp"

    def __init__(self, project_id: str, credentials_path: Optional[str] = None) -> None:
        """Execute __init__ operation.

        Args:
            project_id: The project_id parameter.
            credentials_path: The credentials_path parameter.
        """
        try:
            from google.cloud import secretmanager
        except ImportError as e:
            raise RuntimeError(
                "google-cloud-secret-manager required. Install: pip install fast_secrets[gcp]"
            ) from e
        if credentials_path:
            import os

            os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", credentials_path)
        self._client = secretmanager.SecretManagerServiceClient()
        self._project = project_id

    def _name(self, key: str) -> str:
        """Execute _name operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        return f"projects/{self._project}/secrets/{key}/versions/latest"

    def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
        """Execute get_secret operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        try:
            r = self._client.access_secret_version(name=self._name(key))
            return r.payload.data.decode("utf-8")
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
        parent = f"projects/{self._project}"
        try:
            self._client.create_secret(
                request={
                    "parent": parent,
                    "secret_id": key,
                    "secret": {"replication": {"automatic": {}}},
                }
            )
        except Exception:
            pass  # may already exist
        self._client.add_secret_version(
            request={
                "parent": f"{parent}/secrets/{key}",
                "payload": {"data": value.encode("utf-8")},
            }
        )
