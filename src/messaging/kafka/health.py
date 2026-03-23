"""
Cluster health probes via Kafka Admin API (metadata / ``describe_cluster``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiokafka.admin import AIOKafkaAdminClient


@dataclass
class KafkaClusterHealth:
    """Result of a liveness/readiness style cluster check."""

    ok: bool
    cluster_id: str | None = None
    broker_count: int | None = None
    controller_id: int | None = None
    raw: dict[str, Any] | None = None
    error: str | None = None


async def describe_cluster_health(
    bootstrap_servers: str,
    *,
    request_timeout_ms: int = 5_000,
) -> KafkaClusterHealth:
    """
    Connect with :class:`AIOKafkaAdminClient`, call ``describe_cluster``, and return a summary.

    Suitable for HTTP health endpoints or startup probes when Kafka must be reachable.
    """
    admin = AIOKafkaAdminClient(
        bootstrap_servers=bootstrap_servers,
        request_timeout_ms=request_timeout_ms,
    )
    try:
        await admin.start()
        obj = await admin.describe_cluster()
        brokers = obj.get("brokers") or []
        return KafkaClusterHealth(
            ok=True,
            cluster_id=obj.get("cluster_id"),
            broker_count=len(brokers) if isinstance(brokers, list) else None,
            controller_id=obj.get("controller_id"),
            raw=obj,
        )
    except Exception as exc:
        return KafkaClusterHealth(ok=False, error=str(exc))
    finally:
        try:
            await admin.close()
        except Exception:
            pass
