"""
Unified enqueue entry point for Celery, RQ, and Dramatiq.
"""

from __future__ import annotations

import importlib
from typing import Any, Dict, List, Literal, Optional, Tuple

from fast_platform import JobsConfiguration

from .result import JobEnqueueResult
from .timeout import resolve_job_timeout_seconds


def _enabled_backends(cfg: Any) -> List[Literal["celery", "rq", "dramatiq"]]:
    out: List[Literal["celery", "rq", "dramatiq"]] = []
    if getattr(cfg.celery, "enabled", False):
        out.append("celery")
    if getattr(cfg.rq, "enabled", False):
        out.append("rq")
    if getattr(cfg.dramatiq, "enabled", False):
        out.append("dramatiq")
    return out


def _resolve_backend(requested: Literal["auto", "celery", "rq", "dramatiq"]) -> Literal["celery", "rq", "dramatiq"]:
    cfg = JobsConfiguration().get_config()
    enabled = _enabled_backends(cfg)
    if requested == "auto":
        if len(enabled) == 1:
            return enabled[0]
        if len(enabled) == 0:
            raise RuntimeError("No job backend enabled in JobsConfiguration (celery / rq / dramatiq).")
        raise RuntimeError(
            f"Multiple job backends enabled {enabled}; pass backend='celery'|'rq'|'dramatiq' explicitly."
        )
    if requested not in enabled:
        raise RuntimeError(f"Backend {requested!r} is not enabled in configuration.")
    return requested


def _timeouts_from_cfg(cfg: Any) -> Any:
    return getattr(cfg, "queue_timeouts", None) or {}


def _import_callable(task_name: str) -> Tuple[Any, str, str]:
    """Import ``module.sub:attr`` or ``module.sub.attr`` as callable; return (callable, module, attr)."""
    if ":" in task_name:
        mod_name, attr = task_name.split(":", 1)
    else:
        if "." not in task_name:
            raise ValueError("task_name must be 'package.module:callable' or 'package.module.callable'")
        mod_name, attr = task_name.rsplit(".", 1)
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, attr)
    return fn, mod_name, attr


def enqueue(
    task_or_name: Any,
    *args: Any,
    task_kwargs: Optional[Dict[str, Any]] = None,
    job_kwargs: Optional[Dict[str, Any]] = None,
    queue: Optional[str] = None,
    backend: Literal["auto", "celery", "rq", "dramatiq"] = "auto",
    timeout: Optional[int] = None,
) -> JobEnqueueResult:
    """
    Enqueue a task.

    - **Celery** — pass a **task** object with ``apply_async`` (``@app.task``) or a task name string
      for ``send_task``.
    - **RQ** — pass a **callable** or a string ``module.path:callable`` (see :func:`_import_callable`).
    - **Dramatiq** — pass a **@dramatiq.actor** object (or a duck-typed object with ``send_with_options``).

    ``job_kwargs`` is an alias for ``task_kwargs`` (caller keyword args to the task).
    ``timeout`` overrides ``resolve_job_timeout_seconds`` for this enqueue.
    """
    if task_kwargs is not None and job_kwargs is not None:
        kw = {**job_kwargs, **task_kwargs}
    elif task_kwargs is not None:
        kw = task_kwargs
    elif job_kwargs is not None:
        kw = job_kwargs
    else:
        kw = {}

    b = _resolve_backend(backend)

    if b == "celery":
        return _enqueue_celery(task_or_name, args, kw, queue, timeout)
    if b == "rq":
        return _enqueue_rq(task_or_name, args, kw, queue, timeout)
    return _enqueue_dramatiq(task_or_name, args, kw, queue, timeout)


def _enqueue_celery(
    task_or_name: Any,
    args: Tuple[Any, ...],
    kw: Dict[str, Any],
    queue: Optional[str],
    timeout_override: Optional[int],
) -> JobEnqueueResult:
    try:
        from jobs.celery_app import make_celery_app
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("celery is not installed. pip install fast_jobs[celery]") from e

    cfg = JobsConfiguration().get_config()
    qname = queue or cfg.celery.namespace or "fastmvc"
    timeouts = _timeouts_from_cfg(cfg)
    secs = resolve_job_timeout_seconds(qname, explicit=timeout_override, queue_timeouts=timeouts)
    if secs is None:
        secs = 300

    if hasattr(task_or_name, "apply_async"):
        async_result = task_or_name.apply_async(
            args=args,
            kwargs=kw,
            queue=queue,
            time_limit=secs,
            soft_time_limit=secs,
        )
        return JobEnqueueResult(
            job_id=async_result.id,
            backend="celery",
            queue=queue or qname,
            timeout_seconds=secs,
            raw=async_result,
        )

    app = make_celery_app()
    async_result = app.send_task(
        task_or_name,
        args=args,
        kwargs=kw,
        queue=queue,
        time_limit=secs,
        soft_time_limit=secs,
    )
    return JobEnqueueResult(
        job_id=async_result.id,
        backend="celery",
        queue=queue or qname,
        timeout_seconds=secs,
        raw=async_result,
    )


def _enqueue_rq(
    task_or_name: Any,
    args: Tuple[Any, ...],
    kw: Dict[str, Any],
    queue: Optional[str],
    timeout_override: Optional[int],
) -> JobEnqueueResult:
    try:
        from redis import Redis
        from rq import Queue
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("rq/redis not installed. pip install fast_jobs[rq]") from e

    cfg = JobsConfiguration().get_config()
    qname = queue or cfg.rq.queue_name
    timeouts = _timeouts_from_cfg(cfg)
    secs = resolve_job_timeout_seconds(qname, explicit=timeout_override, queue_timeouts=timeouts)
    if secs is None:
        secs = 300

    redis_url = cfg.rq.redis_url or cfg.rq.connection_url
    conn = Redis.from_url(redis_url)
    rq_queue = Queue(qname, connection=conn)

    if callable(task_or_name) and not isinstance(task_or_name, str):
        job = rq_queue.enqueue_call(func=task_or_name, args=args, kwargs=kw, timeout=secs)
    else:
        if not isinstance(task_or_name, str):
            raise TypeError("RQ enqueue requires a callable or module path string")
        func, _, _ = _import_callable(task_or_name)
        job = rq_queue.enqueue_call(func=func, args=args, kwargs=kw, timeout=secs)

    jid = getattr(job, "id", None)
    if jid is None and callable(getattr(job, "get_id", None)):
        jid = job.get_id()

    return JobEnqueueResult(
        job_id=str(jid) if jid is not None else "",
        backend="rq",
        queue=qname,
        timeout_seconds=secs,
        raw=job,
    )


def _enqueue_dramatiq(
    actor: Any,
    args: Tuple[Any, ...],
    kw: Dict[str, Any],
    queue: Optional[str],
    timeout_override: Optional[int],
) -> JobEnqueueResult:
    try:
        import dramatiq
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("dramatiq is not installed. pip install fast_jobs[dramatiq]") from e

    cfg = JobsConfiguration().get_config()
    qname = queue or cfg.dramatiq.queue_name
    timeouts = _timeouts_from_cfg(cfg)
    secs = resolve_job_timeout_seconds(qname, explicit=timeout_override, queue_timeouts=timeouts)
    if secs is None:
        secs = 300

    if isinstance(actor, dramatiq.Actor) or hasattr(actor, "send_with_options"):
        tl_ms = int(secs * 1000)
        message = actor.send_with_options(
            args=args,
            kwargs=kw,
            queue_name=qname,
            time_limit=tl_ms,
        )
        aname = getattr(actor, "actor_name", None)
        if not isinstance(aname, str):
            aname = getattr(getattr(actor, "fn", None), "__name__", "") or ""
        return JobEnqueueResult(
            job_id=message.message_id,
            backend="dramatiq",
            queue=qname,
            timeout_seconds=secs,
            raw=message,
            dramatiq_queue_name=qname,
            dramatiq_actor_name=str(aname) if aname else None,
        )

    raise TypeError(f"Dramatiq enqueue requires a @dramatiq.actor or send_with_options, got {type(actor)!r}")
