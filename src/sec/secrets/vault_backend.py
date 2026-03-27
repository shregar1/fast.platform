"""HashiCorp Vault secrets backend."""

from __future__ import annotations

from typing import Any, Optional

from .base import ISecretsBackend


class VaultSecretsBackend(ISecretsBackend):
    """Vault KV secrets engine backend."""

    name = "vault"

    def __init__(self, url: str, token: Optional[str] = None, mount_point: str = "secret") -> None:
        """Execute __init__ operation.

        Args:
            url: The url parameter.
            token: The token parameter.
            mount_point: The mount_point parameter.
        """
        try:
            import hvac
        except ImportError as e:
            raise RuntimeError(
                "hvac is required for Vault. Install: pip install fast_secrets[vault]"
            ) from e
        self._client = hvac.Client(url=url, token=token)
        self._mount = mount_point

    def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
        """Execute get_secret operation.

        Args:
            key: The key parameter.

        Returns:
            The result of the operation.
        """
        try:
            r = self._client.secrets.kv.v2.read_secret_version(path=key, mount_point=self._mount)
            data = r.get("data", {}).get("data") or {}
            if not data:
                return None
            return (
                data.get("value") or data.get(key.split("/")[-1]) or next(iter(data.values()), None)
            )
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
        self._client.secrets.kv.v2.create_or_update_secret(
            path=key,
            secret={"value": value},
            mount_point=self._mount,
        )
