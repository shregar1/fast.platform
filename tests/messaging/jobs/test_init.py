"""Tests for jobs."""

from tests.messaging.jobs.abstraction import IJobTests


class TestInit(IJobTests):
    """Represents the TestInit class."""

    def test_imports(self):
        """Execute test_imports operation.

        Returns:
            The result of the operation.
        """
        from messaging.jobs import (
            JobEnqueueResult,
            JobsConfiguration,
            enqueue,
            make_celery_app,
            resolve_job_timeout_seconds,
        )

        assert make_celery_app is not None
        assert JobsConfiguration is not None
        assert JobEnqueueResult is not None
        assert enqueue is not None
        assert resolve_job_timeout_seconds("q", explicit=1) == 1
        import messaging.jobs as fj

        assert fj.__version__ == "0.3.0"
