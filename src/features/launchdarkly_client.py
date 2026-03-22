"""LaunchDarkly feature flags client."""

from __future__ import annotations

from typing import Any, Optional

from .abstraction import IFeatureFlagsClient
from .evaluation import FlagEvaluation, FlagEvaluationReason


def _map_ld_reason(reason_obj: Any) -> FlagEvaluationReason:
    if reason_obj is None:
        return FlagEvaluationReason.UNKNOWN
    s = str(reason_obj).lower()
    if "percentage" in s or "rollout" in s or "bucket" in s:
        return FlagEvaluationReason.PERCENTAGE
    if "rule" in s or "target" in s or "clause" in s:
        return FlagEvaluationReason.RULE
    if "default" in s or "off" in s or "fallthrough" in s:
        return FlagEvaluationReason.DEFAULT
    return FlagEvaluationReason.UNKNOWN


class LaunchDarklyFeatureFlagsClient(IFeatureFlagsClient):
    """LaunchDarkly SDK wrapper."""

    def __init__(self, sdk_key: str, default_user_key: str = "anonymous"):
        try:
            import launchdarkly.server_sdk as ld
        except ImportError as e:
            raise RuntimeError(
                "launchdarkly-server-sdk required. Install: pip install fast_feature_flags[launchdarkly]"
            ) from e
        self._sdk_key = sdk_key
        self._default_key = default_user_key
        self._client = ld.LDClient(sdk_key)
        self._client.wait_for_initialization()

    def _user(self, context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        if not context:
            return {"key": self._default_key}
        key = context.get("key") or context.get("user_key") or self._default_key
        return {"key": key, **{k: v for k, v in context.items() if k not in ("key", "user_key")}}

    def is_enabled(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> bool:
        return self._client.variation(flag_key, self._user(context), False)

    def get_value(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> Any:
        return self._client.variation(flag_key, self._user(context), None)

    def evaluate_with_reason(self, flag_key: str, context: Optional[dict[str, Any]] = None) -> FlagEvaluation:
        user = self._user(context)
        try:
            detail = self._client.variation_detail(flag_key, user, False)
        except Exception:
            return super().evaluate_with_reason(flag_key, context)

        val = getattr(detail, "value", None)
        reason_raw = getattr(detail, "reason", None)
        reason = _map_ld_reason(reason_raw)
        detail_str = str(reason_raw) if reason_raw is not None else None
        return FlagEvaluation(
            enabled=bool(val),
            value=val,
            reason=reason,
            detail=detail_str,
        )
