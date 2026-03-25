from __future__ import annotations

"""Tests for :func:`data.storage.base.build_storage_backend` when backend modules fail to import."""
import builtins
import sys
import types

import pytest

from tests.data_platform.storage.abstraction import IStorageTests


class TestBackendsFactoryImportError(IStorageTests):
    def test_build_storage_backend_import_error_returns_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from data.storage import base as storage_base

        class FakeCfg:
            def __init__(self) -> None:
                self.s3 = types.SimpleNamespace(
                    enabled=True,
                    bucket="b",
                    region="us-east-1",
                    endpoint_url=None,
                    access_key_id=None,
                    secret_access_key=None,
                    base_path="",
                )
                self.gcs = types.SimpleNamespace(
                    enabled=True, bucket="g", credentials_json_path=None, base_path=""
                )
                self.azure_blob = types.SimpleNamespace(
                    enabled=True,
                    container="c",
                    connection_string=None,
                    account_url="http://acc",
                    base_path="",
                )
                self.local = types.SimpleNamespace(enabled=False, base_dir="x", base_url=None)

        monkeypatch.setattr(
            storage_base,
            "StorageConfiguration",
            lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()),
            raising=True,
        )
        real_import = builtins.__import__

        def _fail_backend_import(name: str, *args: object, **kwargs: object):
            if "s3_backend" in name or "gcs_backend" in name or "azure_backend" in name:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fail_backend_import)
        sys.modules.pop("data.storage.s3_backend", None)
        sys.modules.pop("data.storage.gcs_backend", None)
        sys.modules.pop("data.storage.azure_backend", None)
        assert storage_base.build_storage_backend("s3") is None
        assert storage_base.build_storage_backend("gcs") is None
        assert storage_base.build_storage_backend("azure_blob") is None
