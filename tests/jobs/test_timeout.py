"""Tests for timeout resolution."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from config.dto_extras import JobsConfigurationDTO

from jobs.timeout import get_queue_timeouts, resolve_job_timeout_seconds


def test_resolve_explicit_wins():
    assert resolve_job_timeout_seconds("q", explicit=99, queue_timeouts={"q": 1}) == 99


def test_resolve_queue_then_default():
    m = {"default": 10, "mail": 30}
    assert resolve_job_timeout_seconds("mail", queue_timeouts=m) == 30
    assert resolve_job_timeout_seconds("other", queue_timeouts=m) == 10


def test_resolve_none():
    assert resolve_job_timeout_seconds("x", queue_timeouts={}) is None


@patch("jobs.timeout.JobsConfiguration")
def test_get_queue_timeouts(mock_jobs: MagicMock) -> None:
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
