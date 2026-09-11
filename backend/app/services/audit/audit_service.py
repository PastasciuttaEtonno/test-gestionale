"""Servizio audit persistito su PostgreSQL."""

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.security.audit_repository import AuditRepository, AuditRow
from app.schemas.audit.responses import AuditLogListResponse, AuditLogResponse

DEFAULT_LIMIT = 200
MAX_LIMIT = 1000

# Campi del payload scritti da chi tenta l'accesso: possono contenere dati
# personali, o una password digitata nel campo sbagliato.
_CAMPI_PAYLOAD_RISERVATI = ("identificativo",)


class AuditService:
    """Servizio applicativo per il logging di audit."""

    def __init__(self, session: Session) -> None:
        self.audit_repository = AuditRepository(session)

    async def list_events(self, limit: int = DEFAULT_LIMIT) -> AuditLogListResponse:
        """Restituisce le voci dell'audit log, dalla piu recente."""
        rows = await self.audit_repository.list_events(limit)
        return self._to_list_response(rows)

    async def list_events_for_tenant(
        self, tenant_id: str, limit: int = DEFAULT_LIMIT
    ) -> AuditLogListResponse:
        """Restituisce le voci di audit riferibili a un tenant specifico."""
        rows = await self.audit_repository.list_events_by_tenant(tenant_id, limit)
        return self._to_list_response(rows)

    def _to_list_response(self, rows: list[AuditRow]) -> AuditLogListResponse:
        """Converte gli eventi nel payload di risposta.

        La demo pubblica condivide le credenziali admin fra tutti i visitatori:
        li IP, user agent e identificativi digitati al login vengono oscurati,
        altrimenti ogni visitatore leggerebbe quelli degli altri.
        """
        oscura = settings.demo_readonly
        items = [
            AuditLogResponse(
                id=event.id,
                user_id=event.user_id,
                username=username,
                tenant_name=tenant_name,
                event_type=event.event_type,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                payload_json=_oscura_payload(event.payload_json) if oscura else event.payload_json,
                ip_address=None if oscura else event.ip_address,
                user_agent=None if oscura else event.user_agent,
                created_at=event.created_at,
            )
            for event, username, tenant_name in rows
        ]
        return AuditLogListResponse(items=items, total=len(items))


def _oscura_payload(payload: dict | None) -> dict | None:
    """Toglie dal payload i campi scritti liberamente da chi tenta l'accesso."""
    if payload is None:
        return None
    return {k: v for k, v in payload.items() if k not in _CAMPI_PAYLOAD_RISERVATI}
