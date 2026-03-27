"""Module test_enqueue.py."""

from __future__ import annotations

"""Tests for unified enqueue (mocked backends)."""
from unittest.mock import MagicMock, patch

import pytest

from core.dtos import JobsConfigurationDTO
from messaging.jobs.enqueue import enqueue
from tests.messaging.jobs.abstraction import IJobTests


class TestEnqueue(IJobTests):
    """Represents the TestEnqueue class."""

    @staticmethod
    def _cfg(**overrides: object) -> JobsConfigurationDTO:
        """Execute _cfg operation.

        Returns:
            The result of the operation.
        """
        raw = {
            "celery": {"enabled": False, "broker_url": "redis://x", "result_backend": "redis://x"},
            "rq": {
                "enabled": False,
                "redis_url": "redis://localhost:6379/0",
                "queue_name": "default",
            },
            "dramatiq": {"enabled": False, "broker_url": "redis://x", "queue_name": "default"},
            "scheduler": {"enabled": False},
            "queue_timeouts": {"default": 60, "mail": 120},
        }
        raw.update(overrides)
        return JobsConfigurationDTO.model_validate(raw)

    @patch("messaging.jobs.enqueue.JobsConfiguration")
    def test_enqueue_celery_apply_async(self, mock_jobs: MagicMock) -> None:
        """Execute test_enqueue_celery_apply_async operation.

        Args:
            mock_jobs: The mock_jobs parameter.

        Returns:
            The result of the operation.
        """
        cfg = self._cfg(
            celery={"enabled": True, "broker_url": "redis://x", "result_backend": "redis://x"}
        )
        mock_jobs.return_value.get_config.return_value = cfg
        task = MagicMock()
        task.apply_async.return_value = MagicMock(id="celery-id-1")
        r = enqueue(task, 1, 2, backend="celery", queue="mail", job_kwargs={"z": 3})
        task.apply_async.assert_called_once()
        call_kw = task.apply_async.call_args[1]
        assert call_kw["args"] == (1, 2)
        assert call_kw["kwargs"] == {"z": 3}
        assert call_kw["queue"] == "mail"
        assert call_kw["soft_time_limit"] == 120
        assert call_kw["time_limit"] == 120
        assert r.backend == "celery"
        assert r.job_id == "celery-id-1"
        assert r.timeout_seconds == 120

    @patch("messaging.jobs.enqueue.JobsConfiguration")
    @patch("rq.Queue")
    @patch("redis.Redis")
    def test_enqueue_rq_enqueue_call(
        self, _mock_redis: MagicMock, mock_queue_cls: MagicMock, mock_jobs: MagicMock
    ) -> None:
        """Execute test_enqueue_rq_enqueue_call operation.

        Args:
            _mock_redis: The _mock_redis parameter.
            mock_queue_cls: The mock_queue_cls parameter.
            mock_jobs: The mock_jobs parameter.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("redis")
        pytest.importorskip("rq")
        cfg = self._cfg(
            rq={"enabled": True, "redis_url": "redis://localhost:9/0", "queue_name": "default"}
        )
        mock_jobs.return_value.get_config.return_value = cfg
        job = MagicMock(id="rq-job-1")
        mock_queue_cls.return_value.enqueue_call.return_value = job

        def work(a: int, b: int) -> int:
            """Execute work operation.

            Args:
                a: The a parameter.
                b: The b parameter.

            Returns:
                The result of the operation.
            """
            return a + b

        r = enqueue(work, 2, 3, backend="rq", queue="default")
        mock_queue_cls.return_value.enqueue_call.assert_called_once()
        ec_kw = mock_queue_cls.return_value.enqueue_call.call_args[1]
        assert ec_kw["func"] is work
        assert ec_kw["args"] == (2, 3)
        assert ec_kw["timeout"] == 60
        assert r.backend == "rq"
        assert r.job_id == "rq-job-1"

    @patch("messaging.jobs.enqueue.JobsConfiguration")
    def test_enqueue_dramatiq_send_with_options(self, mock_jobs: MagicMock) -> None:
        """Execute test_enqueue_dramatiq_send_with_options operation.

        Args:
            mock_jobs: The mock_jobs parameter.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("dramatiq")
        cfg = self._cfg(
            dramatiq={"enabled": True, "broker_url": "redis://x", "queue_name": "default"}
        )
        mock_jobs.return_value.get_config.return_value = cfg
        actor = MagicMock()
        actor.send_with_options.return_value = MagicMock(message_id="dmq-1")
        r = enqueue(actor, 5, backend="dramatiq", queue="default", timeout=10)
        actor.send_with_options.assert_called_once()
        skw = actor.send_with_options.call_args[1]
        assert skw["args"] == (5,)
        assert skw["kwargs"] == {}
        assert skw["time_limit"] == 10000
        assert r.backend == "dramatiq"
        assert r.job_id == "dmq-1"

    @patch("messaging.jobs.enqueue.JobsConfiguration")
    def test_auto_infer_celery(self, mock_jobs: MagicMock) -> None:
        """Execute test_auto_infer_celery operation.

        Args:
            mock_jobs: The mock_jobs parameter.

        Returns:
            The result of the operation.
        """
        cfg = self._cfg(
            celery={"enabled": True, "broker_url": "redis://x", "result_backend": "redis://x"}
        )
        mock_jobs.return_value.get_config.return_value = cfg
        task = MagicMock()
        task.apply_async.return_value = MagicMock(id="x")
        enqueue(task, backend="auto")
        task.apply_async.assert_called_once()
