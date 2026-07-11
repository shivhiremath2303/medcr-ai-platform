import json
import logging
import sys
import time
from datetime import datetime
from typing import Any, Dict

from app.core.observability.context import get_request_id, get_correlation_id

class StructuredFormatter(logging.Formatter):
    """
    Base formatter for structured logging.
    """
    def __init__(self, app_name: str, app_version: str, environment: str):
        super().__init__()
        self.app_name = app_name
        self.app_version = app_version
        self.environment = environment

    def _get_common_fields(self, record: logging.LogRecord) -> Dict[str, Any]:
        return {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "request_id": get_request_id(),
            "correlation_id": get_correlation_id(),
            "component": record.module,
        }

class JsonFormatter(StructuredFormatter):
    """
    Formats log records as JSON strings.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = self._get_common_fields(record)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)

class ConsoleFormatter(StructuredFormatter):
    """
    Formats log records for human readability in console.
    """
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        request_id = get_request_id() or "no-request-id"

        log_msg = f"{timestamp} | {record.levelname:8} | {request_id} | {record.name} | {record.getMessage()}"

        if record.exc_info:
            log_msg += f"\n{self.formatException(record.exc_info)}"

        return log_msg

def setup_logging(
    app_name: str,
    app_version: str,
    environment: str,
    log_level: str = "INFO",
    json_format: bool = False
) -> None:
    """
    Configures the root logger for the application.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)

    if json_format:
        formatter = JsonFormatter(app_name, app_version, environment)
    else:
        formatter = ConsoleFormatter(app_name, app_version, environment)

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    """
    return logging.getLogger(name)
