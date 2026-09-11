"""Repository audit."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security.audit_log import AuditLog
from app.models.security.tenant import Tenant
from app.models.security.user import User

# Evento di audit con lo username dell'autore e il nome del suo tenant, quando noti.
AuditRow = tuple[AuditLog, str | None, str | None]


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

    async def list_events(self, limit: int) -> list[AuditRow]:
        """Restituisce gli eventi di audit piu recenti, di qualunque tenant."""
        statement = self._select_con_autore().order_by(AuditLog.created_at.desc()).limit(limit)
        return self._righe(statement)

    async def list_events_by_tenant(self, tenant_id: str, limit: int) -> list[AuditRow]:
        """Restituisce gli eventi di audit piu recenti riferibili a utenti del tenant."""
        statement = (
            self._select_con_autore()
            .where(User.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return self._righe(statement)

    def _select_con_autore(self):
        # Outer join: un login fallito su uno username inesistente non ha utente.
        return (
            select(AuditLog, User.username, Tenant.name)
            .outerjoin(User, User.id == AuditLog.user_id)
            .outerjoin(Tenant, Tenant.id == User.tenant_id)
        )

    def _righe(self, statement) -> list[AuditRow]:
        return [
            (event, username, tenant_name)
            for event, username, tenant_name in self.session.execute(statement)
        ]
