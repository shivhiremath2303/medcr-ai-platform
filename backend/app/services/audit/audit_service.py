from typing import Any, Dict, Optional

from app.core.observability.logger import get_logger
from app.domain.models.audit import AuditEvent, AuditEventType

logger = get_logger("security.audit")


class AuditService:
    """
    Coordinates enterprise-grade audit logging.
    Ensures security events are logged with consistent structure and correlation IDs.
    """

    def log(
        self,
        event_type: AuditEventType,
        action: str,
        status: str = "success",
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        event = AuditEvent(
            event_type=event_type,
            action=action,
            status=status,
            user_id=user_id,
            username=username,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # In this phase, we use the structured JSON logger.
        # Future phases can add an AuditRepository for DB persistence.
        log_level = "INFO"
        if status == "failure" or event_type in [
            AuditEventType.ACCESS_DENIED,
            AuditEventType.ACCOUNT_LOCKOUT,
        ]:
            log_level = "WARNING"

        logger.log(
            level=log_level,
            msg=f"Audit Event: {event_type} - {action} ({status})",
            extra={
                "extra_data": {
                    "audit": event.model_dump(),
                    "is_audit_event": True,
                }
            },
        )
