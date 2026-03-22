"""
Datadog integration helpers.

This module configures environment variables for Datadog tracing / APM
based on `config/datadog/config.json`. It is intentionally lightweight:
projects can call `configure_datadog()` once during startup if they want
Datadog to be active.
"""

from __future__ import annotations

import os

from from fast_platform import DatadogConfiguration
from loguru import logger


def configure_datadog() -> None:
    """
    Configure Datadog environment variables and, if available, enable ddtrace.
    """
    cfg = DatadogConfiguration().get_config()
    if not cfg.enabled:
        logger.info("Datadog is disabled in configuration.")
        return

    os.environ.setdefault("DD_ENV", cfg.env)
    os.environ.setdefault("DD_SERVICE", cfg.service)
    if cfg.version:
        os.environ.setdefault("DD_VERSION", cfg.version)
    os.environ.setdefault("DD_AGENT_HOST", cfg.agent_host)
    os.environ.setdefault("DD_TRACE_AGENT_PORT", str(cfg.agent_port))

    logger.info(
        "Configured Datadog environment",
        env=cfg.env,
        service=cfg.service,
        agent_host=cfg.agent_host,
        agent_port=cfg.agent_port,
    )

    try:  # Optional integration
        import ddtrace.auto  # type: ignore  # noqa: F401

        logger.info("ddtrace auto-instrumentation enabled.")
    except Exception:
        logger.warning(
            "ddtrace is not installed; Datadog tracing will not be active. "
            "Install with `pip install ddtrace` to enable."
        )

