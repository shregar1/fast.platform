"""
Mask secret material in strings and nested structures (e.g. before logging config dumps).
"""

from __future__ import annotations

import copy
import json
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Optional, Set, Union


def redact_text(text: str, *secret_values: str, mask: str = "***") -> str:
    """
    Replace occurrences of each non-empty ``secret_values`` substring with ``mask``.

    Longest secrets are applied first so shorter tokens nested inside longer ones do not
    leave partial leaks.
    """
    if not text:
        return text
    values = [v for v in secret_values if v]
    if not values:
        return text
    out = text
    for s in sorted(values, key=len, reverse=True):
        out = out.replace(s, mask)
    return out


def redact_mapping(
    data: Any,
    secret_keys: Union[Set[str], Iterable[str]],
    *,
    mask: str = "***",
    key_predicate: Optional[Callable[[str], bool]] = None,
) -> Any:
    """
    Deep-copy ``data`` (dict / list / tuple / primitives) and replace values whose key
    matches ``secret_keys`` (case-sensitive) or ``key_predicate(name)`` is True.

    Keys are compared at each dict level only (not full JSON paths).
    """
    keys = set(secret_keys) if not isinstance(secret_keys, set) else secret_keys

    def _redact(obj: Any) -> Any:
        if isinstance(obj, Mapping):
            out: MutableMapping[str, Any] = {}
            for k, v in obj.items():
                ks = str(k)
                hide = ks in keys or (key_predicate(ks) if key_predicate else False)
                out[k] = mask if hide else _redact(v)
            return out
        if isinstance(obj, (list, tuple)):
            seq = [_redact(x) for x in obj]
            return type(obj)(seq) if isinstance(obj, tuple) else seq
        return obj

    return _redact(copy.deepcopy(data))


def redact_json_for_log(obj: Any, *secret_values: str, mask: str = "***") -> str:
    """``json.dumps`` with optional ``default=`` handling, then :func:`redact_text` on the string."""
    raw = json.dumps(obj, default=str, ensure_ascii=False)
    return redact_text(raw, *secret_values, mask=mask)
