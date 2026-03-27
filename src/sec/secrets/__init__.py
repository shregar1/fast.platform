"""fast_secrets – Secrets backends (Vault, AWS, GCP) for FastMVC."""

from __future__ import annotations

import importlib.util
import pathlib
import sysconfig

# This package shadows the stdlib ``secrets`` module when ``src`` is on ``sys.path``.
# Starlette imports ``from secrets import token_hex``; re-export it from the stdlib module.
_stdlib_secrets_path = pathlib.Path(sysconfig.get_path("stdlib")) / "secrets.py"
if _stdlib_secrets_path.is_file():
    _spec = importlib.util.spec_from_file_location("_stdlib_secrets", _stdlib_secrets_path)
    if _spec is not None and _spec.loader is not None:
        _stdlib_secrets = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_stdlib_secrets)
        token_hex = _stdlib_secrets.token_hex
    else:

        def token_hex(nbytes: int = 32) -> str:  # pragma: no cover
            """Execute token_hex operation.

            Args:
                nbytes: The nbytes parameter.

            Returns:
                The result of the operation.
            """
            raise RuntimeError("stdlib secrets could not be loaded")

else:

    def token_hex(nbytes: int = 32) -> str:  # pragma: no cover
        """Execute token_hex operation.

        Args:
            nbytes: The nbytes parameter.

        Returns:
            The result of the operation.
        """
        raise RuntimeError("stdlib secrets.py not found")


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
