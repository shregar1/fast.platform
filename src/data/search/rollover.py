"""OpenSearch / Elasticsearch index alias helpers (blue/green rollover)."""

from __future__ import annotations

from typing import Any, List, Optional


def swap_index_alias(
    client: Any,
    *,
    alias: str,
    add_index: str,
    remove_index: Optional[str] = None,
) -> None:
    """Atomically move ``alias`` to ``add_index`` and optionally remove it from ``remove_index``.

    Uses ``indices.update_aliases`` (same on ``opensearch-py`` and ``elasticsearch`` clients).
    Typical blue/green flow: bulk index to ``my_index_v2``, then call with
    ``alias="my_index"``, ``add_index="my_index_v2"``, ``remove_index="my_index_v1"``.
    """
    actions: List[dict[str, Any]] = []
    if remove_index:
        actions.append({"remove": {"index": remove_index, "alias": alias}})
    actions.append({"add": {"index": add_index, "alias": alias}})
    client.indices.update_aliases(body={"actions": actions})
