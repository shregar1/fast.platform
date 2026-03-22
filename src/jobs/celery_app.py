"""
Celery application factory using JobsConfiguration from fast_core.
"""

from __future__ import annotations

from typing import Any, Optional

from fast_core import JobsConfiguration


def make_celery_app(
    namespace: Optional[str] = None,
    broker_url: Optional[str] = None,
    result_backend: Optional[str] = None,
) -> Any:
    """
    Create a Celery app from JobsConfiguration (config/jobs/config.json).

    Pass namespace/broker_url/result_backend to override config.
    """
    try:
        from celery import Celery
    except ImportError:
        raise RuntimeError("celery is not installed. Install with: pip install fast_jobs[celery]")

    cfg = JobsConfiguration().get_config()
    celery_cfg = cfg.celery

    broker = broker_url or celery_cfg.broker_url
    backend = result_backend or celery_cfg.result_backend
    ns = namespace or celery_cfg.namespace

    app = Celery(ns or "fastmvc", broker=broker, backend=backend)
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_default_queue=ns or "fastmvc",
    )
    return app


def get_celery_app_if_enabled() -> Optional[Any]:
    """Return a Celery app instance if Celery is enabled in config, else None."""
    cfg = JobsConfiguration().get_config()
    if not getattr(cfg.celery, "enabled", False):
        return None
    return make_celery_app()
