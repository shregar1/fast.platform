"""Tests for Kafka cluster health probes."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


def test_describe_cluster_health_ok():
    from kafka.health import describe_cluster_health

    fake = {
        "cluster_id": "cid-1",
        "brokers": [{"node_id": 1}, {"node_id": 2}],
        "controller_id": 1,
    }

    async def run():
        with patch("kafka.health.AIOKafkaAdminClient") as mock_cls:
            admin = MagicMock()
            admin.start = AsyncMock()
            admin.close = AsyncMock()
            admin.describe_cluster = AsyncMock(return_value=fake)
            mock_cls.return_value = admin

            h = await describe_cluster_health("localhost:9092")
            assert h.ok is True
            assert h.cluster_id == "cid-1"
            assert h.broker_count == 2
            assert h.controller_id == 1
            admin.start.assert_awaited_once()
            admin.close.assert_awaited_once()

    asyncio.run(run())


def test_describe_cluster_health_error():
    from kafka.health import describe_cluster_health

    async def run():
        with patch("kafka.health.AIOKafkaAdminClient") as mock_cls:
            admin = MagicMock()
            admin.start = AsyncMock(side_effect=RuntimeError("no broker"))
            admin.close = AsyncMock()
            mock_cls.return_value = admin

            h = await describe_cluster_health("localhost:9092")
            assert h.ok is False
            assert "no broker" in (h.error or "")
            admin.close.assert_awaited_once()

    asyncio.run(run())


def test_describe_cluster_health_close_errors_swallowed():
    from kafka.health import describe_cluster_health

    fake = {"cluster_id": "x", "brokers": [], "controller_id": 0}

    async def run():
        with patch("kafka.health.AIOKafkaAdminClient") as mock_cls:
            admin = MagicMock()
            admin.start = AsyncMock()
            admin.describe_cluster = AsyncMock(return_value=fake)
            admin.close = AsyncMock(side_effect=RuntimeError("close failed"))
            mock_cls.return_value = admin

            h = await describe_cluster_health("localhost:9092")
            assert h.ok is True

    asyncio.run(run())
