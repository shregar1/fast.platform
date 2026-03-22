"""Tests for fast_secrets."""

import pytest


def test_imports():
    from fast_secrets import (
        CachedSecretsBackend,
        ISecretsBackend,
        LeasedSecretsBackend,
        RotationCallback,
        SecretsConfiguration,
        SecretsConfigurationDTO,
        build_secrets_backend,
        redact_mapping,
        redact_text,
    )
    assert build_secrets_backend is not None
    assert CachedSecretsBackend is not None
    assert LeasedSecretsBackend is not None
    assert RotationCallback is not None
    assert redact_text("x", "x") == "***"

    import fast_secrets as fs

    assert fs.__version__ == "0.3.0"
