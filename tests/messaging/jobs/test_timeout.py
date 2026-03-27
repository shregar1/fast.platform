"""Module test_timeout.py."""

from __future__ import annotations

"""Tests for timeout resolution."""
from unittest.mock import MagicMock, patch

from fast_platform.core.dtos import JobsConfigurationDTO
from fast_platform.messaging.jobs.timeout import get_queue_timeouts, resolve_job_timeout_seconds
from tests.messaging.jobs.abstraction import IJobTests


class TestTimeout(IJobTests):
    """Represents the TestTimeout class."""

    def test_resolve_explicit_wins(self):
        """Execute test_resolve_explicit_wins operation.

        Returns:
            The result of the operation.
        """
        assert resolve_job_timeout_seconds("q", explicit=99, queue_timeouts={"q": 1}) == 99

    def test_resolve_queue_then_default(self):
        """Execute test_resolve_queue_then_default operation.

        Returns:
            The result of the operation.
        """
        m = {"default": 10, "mail": 30}
        assert resolve_job_timeout_seconds("mail", queue_timeouts=m) == 30
        assert resolve_job_timeout_seconds("other", queue_timeouts=m) == 10

    def test_resolve_none(self):
        """Execute test_resolve_none operation.

        Returns:
            The result of the operation.
        """
        assert resolve_job_timeout_seconds("x", queue_timeouts={}) is None

    @patch("fast_platform.messaging.jobs.timeout.JobsConfiguration")
    def test_get_queue_timeouts(self, mock_jobs: MagicMock) -> None:
        """Execute test_get_queue_timeouts operation.

        Args:
            mock_jobs: The mock_jobs parameter.

        Returns:
            The result of the operation.
        """
        cfg = JobsConfigurationDTO.model_validate(
            {
                "celery": {"enabled": False},
                "rq": {"enabled": False},
                "dramatiq": {"enabled": False},
                "scheduler": {"enabled": False},
                "queue_timeouts": {"default": 7},
            }
        )
        mock_jobs.return_value.get_config.return_value = cfg
        assert get_queue_timeouts() == {"default": 7}
