from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AuditEventType(str, Enum):
    # Authentication
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILURE = "auth.login.failure"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token_refresh"
    TOKEN_REVOKE = "auth.token_revoke"
    ACCOUNT_LOCKOUT = "auth.account_lockout"

    # Authorization
    ACCESS_DENIED = "authz.access_denied"
    OWNERSHIP_VIOLATION = "authz.ownership_violation"

    # Document Operations
    DOC_UPLOAD = "doc.upload"
    DOC_DELETE = "doc.delete"
    DOC_READ = "doc.read"

    # AI Operations
    AI_QUERY = "ai.query"
    AI_ANALYSIS = "ai.analysis"

    # Security Protections
    RATE_LIMIT_EXCEEDED = "security.rate_limit_exceeded"
    PAYLOAD_TOO_LARGE = "security.payload_too_large"
    HOST_VIOLATION = "security.host_violation"

    # Administrative
    ADMIN_CACHE_FLUSH = "admin.cache_flush"
    ADMIN_SETTINGS_CHANGE = "admin.settings_change"


class AuditEvent(BaseModel):
    event_type: AuditEventType
    user_id: Optional[str] = None
    username: Optional[str] = None
    resource_id: Optional[str] = None
    action: str
    status: str  # success, failure
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
