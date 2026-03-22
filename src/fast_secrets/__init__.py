"""
fast_secrets – Secrets backends (Vault, AWS, GCP) for FastMVC.
"""

from fast_platform import SecretsConfiguration, SecretsConfigurationDTO

from .base import ISecretsBackend, build_secrets_backend
from .cache import CachedSecretsBackend, RotationCallback
from .lease import LeasedSecretsBackend
from .redact import redact_json_for_log, redact_mapping, redact_text

__version__ = "0.3.0"

__all__ = [
    "CachedSecretsBackend",
    "ISecretsBackend",
    "LeasedSecretsBackend",
    "RotationCallback",
    "SecretsConfiguration",
    "SecretsConfigurationDTO",
    "build_secrets_backend",
    "redact_json_for_log",
    "redact_mapping",
    "redact_text",
]
