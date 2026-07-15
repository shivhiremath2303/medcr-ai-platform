from abc import ABC, abstractmethod

from app.domain.models.audit import AuditEvent


class AuditRepository(ABC):
    """
    Interface for persisting security audit logs.
    In an enterprise system, this often targets a WORM (Write Once Read Many) storage
    or a dedicated security logging service.
    """

    @abstractmethod
    def log_event(self, event: AuditEvent) -> None:
        """Persist an audit event."""
        pass
