"""Module test_backends_abstract.py."""

from __future__ import annotations

"""Tests for :class:`sec.secrets.base.ISecretsBackend` default abstract behavior."""
from typing import Any, Optional

import pytest

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsAbstract(ISecretsTests):
    """Represents the TestBackendsAbstract class."""

    def test_is_secrets_backend_abstract_methods_raise_not_implemented(self) -> None:
        """Execute test_is_secrets_backend_abstract_methods_raise_not_implemented operation.

        Returns:
            The result of the operation.
        """
        from sec.secrets.base import ISecretsBackend

        class DummyBackend(ISecretsBackend):
            """Represents the DummyBackend class."""

            name = "dummy"

            def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
                """Execute get_secret operation.

                Args:
                    key: The key parameter.

                Returns:
                    The result of the operation.
                """
                return super().get_secret(key, **kwargs)

            def set_secret(self, key: str, value: str) -> None:
                """Execute set_secret operation.

                Args:
                    key: The key parameter.
                    value: The value parameter.

                Returns:
                    The result of the operation.
                """
                return super().set_secret(key, value)

        b = DummyBackend()
        with pytest.raises(NotImplementedError):
            b.get_secret("k")
        with pytest.raises(NotImplementedError):
            b.set_secret("k", "v")
