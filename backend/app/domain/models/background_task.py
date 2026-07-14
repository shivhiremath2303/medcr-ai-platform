from datetime import UTC, datetime
from enum import Enum, StrEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class TaskPriority(StrEnum):
    HIGH = "high"  # Real-time user interactions
    DEFAULT = "default"  # Document ingestion
    LOW = "low"  # Periodic cleanup, optimization


class BackgroundTask(BaseModel):
    """
    Enterprise Background Task Model (Milestone 10.3.2).
    """

    model_config = ConfigDict(use_enum_values=True)

    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.DEFAULT
    payload: Dict[str, Any] = Field(default_factory=dict)
    result: Any | None = None
    error: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
