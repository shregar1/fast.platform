from __future__ import annotations
"""Thin autocomplete API over :class:`~fast_search.base.ISearchBackend`."""

from ...core.constants import DEFAULT_PAGE_SIZE

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .base import ISearchBackend


def suggest_autocomplete(
    backend: ISearchBackend,
    index_name: str,
    prefix: str,
    *,
    field: str = "title",
    limit: int = DEFAULT_PAGE_SIZE,
) -> List[str]:
    """Return distinct string completions for ``prefix`` using the backend's :meth:`~ISearchBackend.suggest`.

    Backends may use native prefix queries (e.g. OpenSearch) or the default
    :meth:`~ISearchBackend.suggest` implementation (search + dedupe).
    """
    return backend.suggest(index_name, prefix, field=field, limit=limit)
