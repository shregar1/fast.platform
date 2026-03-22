"""
fast_jobs – Background jobs (Celery, RQ, Dramatiq) for FastMVC.
"""

from fast_core import JobsConfiguration, JobsConfigurationDTO

from .cancel import CancelJobResult, cancel_job
from .celery_app import get_celery_app_if_enabled, make_celery_app
from .enqueue import enqueue
from .result import JobEnqueueResult, JobStatus, JobStatusSnapshot, get_job_status
from .schedule import (
    CronScheduleDTO,
    celery_crontab_schedule,
    dramatiq_periodiq_cron,
    parse_cron_fields,
    rq_scheduler_cron,
)
from .timeout import get_queue_timeouts, resolve_job_timeout_seconds

__version__ = "0.3.0"

__all__ = [
    "CancelJobResult",
    "CronScheduleDTO",
    "JobEnqueueResult",
    "JobStatus",
    "JobStatusSnapshot",
    "JobsConfiguration",
    "JobsConfigurationDTO",
    "cancel_job",
    "celery_crontab_schedule",
    "dramatiq_periodiq_cron",
    "enqueue",
    "get_celery_app_if_enabled",
    "get_job_status",
    "get_queue_timeouts",
    "make_celery_app",
    "parse_cron_fields",
    "resolve_job_timeout_seconds",
    "rq_scheduler_cron",
]
