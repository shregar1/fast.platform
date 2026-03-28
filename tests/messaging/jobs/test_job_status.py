"""Module test_job_status.py."""

from __future__ import annotations

"""Tests for :mod:`messaging.jobs.result.get_job_status` (mocked Celery)."""
from unittest.mock import MagicMock, patch

import pytest

from fast_platform.messaging.jobs.result import JobStatus, get_job_status
from tests.messaging.jobs.abstraction import IJobTests


class TestJobStatus(IJobTests):
    """Represents the TestJobStatus class."""

    def test_get_job_status_celery(self) -> None:
        """Execute test_get_job_status_celery operation.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("celery")
        with patch("celery.result.AsyncResult") as mock_ar_cls, \
             patch("fast_platform.messaging.jobs.celery_app.make_celery_app"):
            mock_ar = MagicMock()
            mock_ar.state = "SUCCESS"
            mock_ar.result = {"ok": True}
            mock_ar_cls.return_value = mock_ar
            snap = get_job_status("jid", "celery")
            assert snap.status == JobStatus.SUCCESS
            assert snap.result == {"ok": True}

