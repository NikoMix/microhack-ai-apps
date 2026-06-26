"""
OpenTelemetry setup for the Zava AI Agent Platform — Python track.

When APPLICATIONINSIGHTS_CONNECTION_STRING is set, telemetry is exported to
Azure Monitor (Application Insights). Otherwise, a no-op OTEL setup is used
so the rest of the code can always call trace APIs.

Usage
-----
Call ``configure_telemetry()`` once during app startup (lifespan).
Call ``get_trace_id()`` inside a request handler to retrieve the current span's
trace ID for inclusion in API responses.
"""

from __future__ import annotations

import logging

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

logger = logging.getLogger(__name__)

_configured = False


def configure_telemetry(connection_string: str | None = None) -> None:
    """Configure OpenTelemetry.

    If *connection_string* is provided (or APPLICATIONINSIGHTS_CONNECTION_STRING
    env var is set), telemetry is exported to Azure Monitor. Otherwise, a
    no-op provider is installed so ``get_trace_id()`` never raises.
    """
    global _configured  # noqa: PLW0603
    if _configured:
        return
    _configured = True

    if connection_string:
        try:
            # azure-monitor-opentelemetry bundles the full OTEL SDK and
            # automatically wires up the Azure Monitor exporter.
            from azure.monitor.opentelemetry import configure_azure_monitor

            configure_azure_monitor(
                connection_string=connection_string,
                enable_live_metrics=False,  # keep overhead low for labs
            )
            logger.info("Azure Monitor OpenTelemetry configured.")
        except ImportError:
            logger.warning(
                "azure-monitor-opentelemetry not installed; falling back to no-op telemetry."
            )
            _install_noop_provider()
    else:
        logger.info(
            "APPLICATIONINSIGHTS_CONNECTION_STRING not set; "
            "using no-op telemetry (traceId will be zeros)."
        )
        _install_noop_provider()


def _install_noop_provider() -> None:
    """Install a minimal SDK TracerProvider so spans are created (but not exported)."""
    provider = TracerProvider()
    trace.set_tracer_provider(provider)


def get_tracer(name: str = "zava.api") -> trace.Tracer:
    """Return the OTEL tracer for *name*."""
    return trace.get_tracer(name)


def get_trace_id() -> str:
    """Return the current span's trace ID as a 32-char hex string.

    Returns all-zeros if no active span exists (e.g. in tests).
    """
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx and ctx.is_valid:
        return format(ctx.trace_id, "032x")
    return "0" * 32
