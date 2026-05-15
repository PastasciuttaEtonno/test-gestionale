"""Servizio audit persistito su PostgreSQL."""

from sqlalchemy.orm import Session

from app.repositories.security.audit_repository import AuditRepository
from app.schemas.audit.responses import AuditLogListResponse, AuditLogResponse


class AuditService:
    """Servizio applicativo per il logging di audit."""

    def __init__(self, session: Session) -> None:
        self.audit_repository = AuditRepository(session)

    async def list_events(self) -> AuditLogListResponse:
        """Restituisce le voci dell'audit log."""
        events = await self.audit_repository.list_events()
        return self._to_list_response(events)

    async def list_events_for_tenant(self, tenant_id: str) -> AuditLogListResponse:
        """Restituisce le voci di audit riferibili a un tenant specifico."""
        events = await self.audit_repository.list_events_by_tenant(tenant_id)
        return self._to_list_response(events)

    def _to_list_response(self, events: list) -> AuditLogListResponse:
        """Converte una collezione ORM di eventi nel payload di risposta."""
        items = [
            AuditLogResponse(
                id=event.id,
                user_id=event.user_id,
                event_type=event.event_type,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                payload_json=event.payload_json,
                ip_address=event.ip_address,
                user_agent=event.user_agent,
                created_at=event.created_at,
            )
            for event in events
        ]
        return AuditLogListResponse(items=items, total=len(items))
