"""Repository audit."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security.audit_log import AuditLog
from app.models.security.user import User


class AuditRepository:
    """Repository per gli eventi di audit."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def log_event(self, audit_log: AuditLog) -> AuditLog:
        """Salva un evento di audit."""
        self.session.add(audit_log)
        self.session.flush()
        self.session.refresh(audit_log)
        return audit_log

    async def list_events(self) -> list[AuditLog]:
        """Restituisce gli eventi di audit."""
        statement = select(AuditLog).order_by(AuditLog.created_at.desc())
        return list(self.session.scalars(statement).all())

    async def list_events_by_tenant(self, tenant_id: str) -> list[AuditLog]:
        """Restituisce gli eventi di audit riferibili a utenti del tenant."""
        statement = (
            select(AuditLog)
            .join(User, User.id == AuditLog.user_id)
            .where(User.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
        )
        return list(self.session.scalars(statement).all())
