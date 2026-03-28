"""Module test_cancel_job.py."""

from __future__ import annotations

"""Tests for :mod:`messaging.jobs.cancel` (mocked backends)."""
from unittest.mock import MagicMock, patch

import pytest


from fast_platform.messaging.jobs.cancel import CancelJobResult, cancel_job
from tests.messaging.jobs.abstraction import IJobTests


class TestCancelJob(IJobTests):
    """Represents the TestCancelJob class."""

    def test_cancel_dramatiq_unsupported(self) -> None:
        """Execute test_cancel_dramatiq_unsupported operation.

        Returns:
            The result of the operation.
        """
        r = cancel_job("mid", "dramatiq")
        assert isinstance(r, CancelJobResult)
        assert r.cancelled is False
        assert r.backend == "dramatiq"

    def test_cancel_celery(self) -> None:
        """Execute test_cancel_celery operation.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("celery")
        with patch("celery.result.AsyncResult") as mock_ar_cls, \
             patch("fast_platform.messaging.jobs.celery_app.make_celery_app"):
            mock_inst = MagicMock()
            mock_ar_cls.return_value = mock_inst
            r = cancel_job("jid", "celery")
            assert r.cancelled is True
            mock_inst.revoke.assert_called_once()

    def test_cancel_rq(self) -> None:
        """Execute test_cancel_rq operation.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("rq")
        with patch("rq.job.Job") as mock_job_cls:
            mock_job = MagicMock()
            mock_job_cls.fetch.return_value = mock_job
            conn = MagicMock()
            r = cancel_job("jid", "rq", rq_connection=conn)
            assert r.cancelled is True
            mock_job.cancel.assert_called_once()
