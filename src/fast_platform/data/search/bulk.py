"""Batch indexing with configurable batch size and per-batch error aggregation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from .base import ISearchBackend


@dataclass(slots=True)
class BulkIndexError:
    """One failed batch."""

    batch_index: int
    message: str
    documents_in_batch: int
    exception: Optional[BaseException] = None


@dataclass(slots=True)
class BulkIndexResult:
    """Outcome of :func:`bulk_index_documents`."""

    total_documents: int
    batch_size: int
    batches_attempted: int
    batches_succeeded: int
    batches_failed: int
    errors: List[BulkIndexError] = field(default_factory=list)


def bulk_index_documents(
    backend: ISearchBackend,
    index_name: str,
    documents: List[dict[str, Any]],
    *,
    batch_size: int = 100,
    stop_on_error: bool = False,
) -> BulkIndexResult:
    """Index ``documents`` in chunks of ``batch_size`` via :meth:`~fast_search.base.ISearchBackend.index_documents`.

    On failure, the error is recorded and the next batch is attempted unless ``stop_on_error`` is True.
    """
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")

    total = len(documents)
    errors: List[BulkIndexError] = []
    succeeded = 0
    attempted = 0
    failed = 0

    for i in range(0, total, batch_size):
        batch = documents[i : i + batch_size]
        bi = i // batch_size
        attempted += 1
        try:
            backend.index_documents(index_name, batch)
            succeeded += 1
        except Exception as e:
            failed += 1
            errors.append(
                BulkIndexError(
                    batch_index=bi,
                    message=str(e),
                    documents_in_batch=len(batch),
                    exception=e,
                )
            )
            if stop_on_error:
                break

    return BulkIndexResult(
        total_documents=total,
        batch_size=batch_size,
        batches_attempted=attempted,
        batches_succeeded=succeeded,
        batches_failed=failed,
        errors=errors,
    )
