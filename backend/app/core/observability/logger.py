import json
import logging
import random
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from opentelemetry import trace

from app.core.observability.context import (
    get_correlation_id,
    get_request_id,
    get_user_id,
)

# Sensitive keys that should be masked in logs
SENSITIVE_KEYS = {
    "password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
    "gemini_api_key",
    "jwt_secret_key",
    "private_key",
    "ssn",
    "credit_card",
}


class SamplingFilter(logging.Filter):
    """
    Log filter to reduce volume by sampling successful logs.
    Errors are always logged.
    """

    def __init__(self, sample_rate: float = 1.0):
        super().__init__()
        self.sample_rate = sample_rate

    def filter(self, record: logging.LogRecord) -> bool:
        # Always log ERRORS and above
        if record.levelno >= logging.ERROR:
            return True

        # Audit events are never sampled (always logged)
        if hasattr(record, "extra_data") and record.extra_data.get("is_audit_event"):
            return True

        if self.sample_rate >= 1.0:
            return True
        # This is volume sampling, not a security decision.
        return random.random() < self.sample_rate  # noqa: S311


class EnterpriseLoggingFormatter(logging.Formatter):
    """
    Base formatter for Enterprise-grade logging.
    Standardizes schema and handles context propagation.
    """

    def __init__(self, app_name: str, app_version: str, environment: str):
        super().__init__()
        self.app_name = app_name
        self.app_version = app_version
        self.environment = environment

    def _get_trace_context(self) -> Dict[str, str]:
        """Extracts OTel trace context."""
        span = trace.get_current_span()
        if not span or not span.get_span_context().is_valid:
            return {}

        ctx = span.get_span_context()
        return {
            "trace_id": format(ctx.trace_id, "032x"),
            "span_id": format(ctx.span_id, "16x"),
        }

    def _mask_sensitive_data(self, data: Any) -> Any:
        """Recursively masks sensitive keys in dictionaries."""
        if isinstance(data, dict):
            return {
                k: (
                    "***MASKED***"
                    if k.lower() in SENSITIVE_KEYS
                    or any(s in k.lower() for s in ["key", "secret", "token"])
                    else self._mask_sensitive_data(v)
                )
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        return data

    def _get_common_fields(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Builds the core structured log schema aligned with ECS."""
        trace_ctx = self._get_trace_context()

        return {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "log.level": record.levelname,
            "log.logger": record.name,
            "log.origin.function": record.funcName,
            "log.origin.file.line": record.lineno,
            "message": record.getMessage(),
            "service.name": self.app_name,
            "service.version": self.app_version,
            "service.environment": self.environment,
            "event.module": record.module,
            # Correlation IDs
            "trace.id": trace_ctx.get("trace_id"),
            "span.id": trace_ctx.get("span_id"),
            "request.id": get_request_id(),
            "correlation.id": get_correlation_id(),
            "user.id": get_user_id(),
        }


class EnterpriseJsonFormatter(EnterpriseLoggingFormatter):
    """
    Production JSON Formatter.
    Implements Milestone 10.2.3.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = self._get_common_fields(record)

        # Handle exceptions
        if record.exc_info:
            log_data["error.stack_trace"] = self.formatException(record.exc_info)
            log_data["error.message"] = str(record.exc_info[1])
            log_data["error.type"] = record.exc_info[0].__name__

        # Merge extra data and mask it
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            masked_extra = self._mask_sensitive_data(record.extra_data)
            log_data.update(masked_extra)

        # Also check for standard 'extra' passed to logger.info(..., extra={})
        reserved = {
            "args",
            "asctime",
            "created",
            "exc_info",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
            "extra_data",
        }

        custom_extra = {
            k: v
            for k, v in record.__dict__.items()
            if k not in reserved and not k.startswith("_")
        }
        if custom_extra:
            log_data.update(self._mask_sensitive_data(custom_extra))

        return json.dumps(log_data)


class EnterpriseConsoleFormatter(EnterpriseLoggingFormatter):
    """
    Development Console Formatter with human-readable output.
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        request_id = get_request_id() or "none"
        trace_ctx = self._get_trace_context()
        trace_id = trace_ctx.get("trace_id", "none")[:8]

        level_color = self._get_level_color(record.levelno)
        reset = "\033[0m"

        log_msg = (
            f"{timestamp} | {level_color}{record.levelname:8}{reset} | "
            f"req:{request_id[:8]} | trc:{trace_id} | "
            f"\033[1;30m{record.name}\033[0m: {record.getMessage()}"
        )

        if record.exc_info:
            log_msg += f"\n\033[0;31m{self.formatException(record.exc_info)}{reset}"

        return log_msg

    def _get_level_color(self, levelno: int) -> str:
        if levelno >= logging.ERROR:
            return "\033[1;31m"  # Bold Red
        if levelno >= logging.WARNING:
            return "\033[1;33m"  # Bold Yellow
        if levelno >= logging.INFO:
            return "\033[1;32m"  # Bold Green
        return "\033[1;34m"  # Bold Blue


def setup_logging(
    app_name: str,
    app_version: str,
    environment: str,
    log_level: str = "INFO",
    json_format: bool = False,
    sample_rate: float = 1.0,
) -> None:
    """
    Configures centralized structured logging for the application.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)

    if json_format or environment == "production":
        formatter = EnterpriseJsonFormatter(app_name, app_version, environment)
        # Apply sampling in production only for JSON logs
        if sample_rate < 1.0:
            handler.addFilter(SamplingFilter(sample_rate))
    else:
        formatter = EnterpriseConsoleFormatter(app_name, app_version, environment)

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Suppress noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("opentelemetry").setLevel(logging.ERROR)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    """
    return logging.getLogger(name)
