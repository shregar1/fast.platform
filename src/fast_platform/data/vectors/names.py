"""Helpers for namespace- or tenant-scoped collection / index names.

Backends differ in allowed characters and length; these helpers produce a
portable, deterministic string suitable for Pinecone indexes, Qdrant collections,
and Weaviate class names in typical setups.
"""

from __future__ import annotations

import re

__all__ = ["VectorCollectionNamesUtility"]


class VectorCollectionNamesUtility:
    """Normalize and compose vector store collection / index names."""

    _SEGMENT_SANITIZE = re.compile(r"[^a-z0-9_-]+")
    _COLLAPSE = re.compile(r"[-_]{2,}")

    @staticmethod
    def sanitize_collection_segment(segment: str, *, fallback: str = "default") -> str:
        """Normalize one path component for use in a collection name.

        Lowercases, strips, replaces disallowed characters with a single hyphen,
        and trims leading/trailing separators. Empty or invalid input becomes
        ``fallback``.
        """
        s = (segment or "").strip().lower()
        s = VectorCollectionNamesUtility._SEGMENT_SANITIZE.sub("-", s)
        s = VectorCollectionNamesUtility._COLLAPSE.sub("-", s).strip("-_")
        return s if s else fallback

    @staticmethod
    def prefixed_collection_name(
        namespace: str,
        name: str,
        *,
        separator: str = "__",
        max_length: int = 255,
    ) -> str:
        """Build a stable collection (or index) name with a namespace / tenant prefix.

        ``namespace`` is typically a tenant id, org slug, or environment key;
        ``name`` is the logical index or collection (e.g. ``"documents"``).

        The separator defaults to ``"__"`` so the boundary stays visible in logs and
        UIs. The combined string is truncated to ``max_length`` (Qdrant allows up
        to 255 characters for collection names).

        Examples::

            VectorCollectionNamesUtility.prefixed_collection_name("acme-corp", "kb-articles")
            # -> "acme-corp__kb-articles"

            VectorCollectionNamesUtility.prefixed_collection_name("tenant_42", "docs", separator="_")
            # -> "tenant_42_docs"
        """
        if not separator or not separator.strip():
            raise ValueError("separator must be non-empty")

        ns = VectorCollectionNamesUtility.sanitize_collection_segment(namespace, fallback="ns")
        base = VectorCollectionNamesUtility.sanitize_collection_segment(name, fallback="collection")

        out = f"{ns}{separator}{base}"
        if len(out) <= max_length:
            return out
        if len(ns) >= max_length:
            return ns[:max_length]
        if len(ns) + len(separator) > max_length:
            return ns[:max_length]
        rest = max_length - len(ns) - len(separator)
        return f"{ns}{separator}{base[:rest]}"
