"""
Offline JSON snapshot feature flag client (no network).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .abstraction import IFeatureFlagsClient
from .evaluation import FlagEvaluation, FlagEvaluationReason


def load_snapshot_from_path(path: str | Path) -> Dict[str, Any]:
    """
    Load and parse snapshot JSON from disk.

    If the root object has a ``flags`` object, its keys are merged to the top level so
    ``data["my_flag"]`` works as well as ``data["flags"]["my_flag"]``.
    """
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("snapshot root must be a JSON object")
    inner = data.get("flags")
    if isinstance(inner, dict):
        out: Dict[str, Any] = dict(inner)
        for k, v in data.items():
            if k != "flags":
                out[k] = v
        return out
    return data


class SnapshotFeatureFlagsClient(IFeatureFlagsClient):
    """
    Evaluate flags from a JSON file.

    Supported shapes:

    - ``{"flags": {"k": true}}`` or ``{"flags": {"k": {"enabled": true, "value": "x"}}}``
    - Flat ``{"k": true}`` or ``{"k": {"enabled": true, "reason": "rule", "value": null}}``
    - Per-flag optional ``reason`` (string) mapped to :class:`FlagEvaluationReason` when known.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data
        self._flags = self._normalize(data)

    @classmethod
    def from_path(cls, path: str | Path) -> SnapshotFeatureFlagsClient:
        return cls(load_snapshot_from_path(path))

    @staticmethod
    def _normalize(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        raw = data.get("flags", data)
        if not isinstance(raw, dict):
            raise ValueError("snapshot must be a JSON object")
        out: Dict[str, Dict[str, Any]] = {}
        for k, v in raw.items():
            if isinstance(v, dict):
                en = v.get("enabled", v.get("value") is not None)
                if "enabled" not in v and "value" in v:
                    en = True
                out[k] = {
                    "enabled": bool(en),
                    "value": v.get("value"),
                    "reason": v.get("reason"),
                }
            else:
                out[k] = {"enabled": bool(v), "value": None, "reason": None}
        return out

    def is_enabled(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> bool:
        ent = self._flags.get(flag_key)
        if ent is None:
            return False
        return bool(ent["enabled"])

    def get_value(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> Any:
        ent = self._flags.get(flag_key)
        if ent is None:
            return None
        if ent.get("value") is not None:
            return ent["value"]
        return ent["enabled"]

    def evaluate_with_reason(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> FlagEvaluation:
        ent = self._flags.get(flag_key)
        if ent is None:
            return FlagEvaluation(False, None, FlagEvaluationReason.DEFAULT, detail="flag_missing_in_snapshot")

        raw_reason = ent.get("reason")
        reason = FlagEvaluationReason.SNAPSHOT
        detail: Optional[str] = None
        if isinstance(raw_reason, str):
            rl = raw_reason.lower().strip()
            if rl in ("rule", "rules", "target", "targeting"):
                reason = FlagEvaluationReason.RULE
                detail = raw_reason
            elif rl in ("percentage", "rollout", "rollout_percentage"):
                reason = FlagEvaluationReason.PERCENTAGE
                detail = raw_reason
            elif rl in ("default",):
                reason = FlagEvaluationReason.DEFAULT
            else:
                detail = raw_reason

        return FlagEvaluation(
            enabled=bool(ent["enabled"]),
            value=ent.get("value") if ent.get("value") is not None else ent["enabled"],
            reason=reason,
            detail=detail,
        )
