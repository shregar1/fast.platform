from __future__ import annotations
"""Bulk index API."""
from tests.data_platform.search.abstraction import ISearchTests



from typing import Any, List, Optional

import pytest

from search.base import ISearchBackend
from search.bulk import bulk_index_documents


class TestBulk(ISearchTests):
    class FlakyBackend(ISearchBackend):
        name = "flaky"

        def __init__(self, fail_batches: set[int]) -> None:
            self.fail_batches = fail_batches
            self.batches: list[list[dict[str, Any]]] = []

        def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
            bi = len(self.batches)
            self.batches.append(documents)
            if bi in self.fail_batches:
                raise RuntimeError(f"batch {bi} failed")

        def search(
            self,
            index_name: str,
            query: str,
            *,
            limit: int = 20,
            offset: int = 0,
            filter: Optional[dict[str, Any]] = None,
        ) -> List[dict[str, Any]]:
            return []

        def delete_index(self, index_name: str) -> None:
            pass

    def test_bulk_index_success_and_errors(self) -> None:
        b = self.FlakyBackend(fail_batches={1})
        docs = [{"i": i} for i in range(5)]
        r = bulk_index_documents(b, "idx", docs, batch_size=2)
        assert r.total_documents == 5
        assert r.batch_size == 2
        assert r.batches_attempted == 3
        assert r.batches_succeeded == 2
        assert r.batches_failed == 1
        assert len(r.errors) == 1
        assert r.errors[0].batch_index == 1
        assert r.errors[0].documents_in_batch == 2

    def test_bulk_index_stop_on_error(self) -> None:
        b = self.FlakyBackend(fail_batches={0})
        docs = [{"i": i} for i in range(4)]
        r = bulk_index_documents(b, "idx", docs, batch_size=2, stop_on_error=True)
        assert r.batches_attempted == 1
        assert r.batches_failed == 1

    def test_bulk_index_batch_size_invalid(self) -> None:
        b = self.FlakyBackend(fail_batches=set())
        with pytest.raises(ValueError):
            bulk_index_documents(b, "idx", [], batch_size=0)
