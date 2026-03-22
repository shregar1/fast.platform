from __future__ import annotations

"""Tests for :class:`secrets.base.ISecretsBackend` default abstract behavior."""
from typing import Any, Optional

import pytest

from tests.sec.secrets.abstraction import ISecretsTests


class TestBackendsAbstract(ISecretsTests):
    def test_is_secrets_backend_abstract_methods_raise_not_implemented(self) -> None:
        from secrets.base import ISecretsBackend

        class DummyBackend(ISecretsBackend):
            name = "dummy"

            def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
                return super().get_secret(key, **kwargs)

            def set_secret(self, key: str, value: str) -> None:
                return super().set_secret(key, value)

        b = DummyBackend()
        with pytest.raises(NotImplementedError):
            b.get_secret("k")
        with pytest.raises(NotImplementedError):
            b.set_secret("k", "v")
