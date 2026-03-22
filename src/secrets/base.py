"""
Secrets backend interface and factory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from from fast_platform import SecretsConfiguration


class ISecretsBackend(ABC):
    """Interface for secrets backends (Vault, AWS Secrets Manager, GCP)."""

    name: str

    @abstractmethod
    def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
        """Get secret value by key/path. Return None if not found.

        Backends ignore unknown kwargs. :class:`~fast_secrets.cache.CachedSecretsBackend`
        accepts ``force_refresh=True`` to bypass the TTL cache.
        """
        raise NotImplementedError

    @abstractmethod
    def set_secret(self, key: str, value: str) -> None:
        """Set secret value."""
        raise NotImplementedError


def build_secrets_backend(backend: str = "vault") -> Optional[ISecretsBackend]:
    """
    Build a secrets backend from SecretsConfiguration (config/secrets/config.json).
    backend: "vault" | "aws" | "gcp"
    """
    cfg = SecretsConfiguration().get_config()

    if backend == "vault" and getattr(cfg.vault, "enabled", False) and cfg.vault.url:
        try:
            from .vault_backend import VaultSecretsBackend
            return VaultSecretsBackend(
                url=cfg.vault.url,
                token=cfg.vault.token,
                mount_point=cfg.vault.mount_point or "secret",
            )
        except ImportError:
            return None

    if backend == "aws" and getattr(cfg.aws, "enabled", False):
        try:
            from .aws_backend import AwsSecretsBackend
            return AwsSecretsBackend(
                region=cfg.aws.region,
                access_key_id=cfg.aws.access_key_id,
                secret_access_key=cfg.aws.secret_access_key,
                prefix=cfg.aws.prefix or "",
            )
        except ImportError:
            return None

    if backend == "gcp" and getattr(cfg.gcp, "enabled", False) and cfg.gcp.project_id:
        try:
            from .gcp_backend import GcpSecretsBackend
            return GcpSecretsBackend(
                project_id=cfg.gcp.project_id,
                credentials_path=cfg.gcp.credentials_json_path,
            )
        except ImportError:
            return None

    return None
