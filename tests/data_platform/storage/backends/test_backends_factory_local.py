"""Module test_backends_factory_local.py."""

from __future__ import annotations

"""Tests for :func:`data.storage.base.build_storage_backend` (local)."""
import types

import pytest

from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsFactoryLocal(IStorageTests):
    """Represents the TestBackendsFactoryLocal class."""

    def test_storage_factory_selects_local_backend(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path
    ) -> None:
        """Execute test_storage_factory_selects_local_backend operation.

        Args:
            monkeypatch: The monkeypatch parameter.
            tmp_path: The tmp_path parameter.

        Returns:
            The result of the operation.
        """
        from fast_platform.data.storage import base as storage_base

        class FakeCfg:
            """Represents the FakeCfg class."""

            def __init__(self) -> None:
                """Execute __init__ operation."""
                self.s3 = types.SimpleNamespace(enabled=False, bucket=None)
                self.gcs = types.SimpleNamespace(enabled=False, bucket=None)
                self.azure_blob = types.SimpleNamespace(enabled=False, container=None)
                self.local = types.SimpleNamespace(
                    enabled=True, base_dir=str(tmp_path / "storage"), base_url=None
                )

        monkeypatch.setattr(
            storage_base,
            "StorageConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        backend = storage_base.build_storage_backend("local")
        assert backend is not None
        assert backend.name == "local"
