"""Route tenant admin."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps.auth import require_tenant_admin
from app.core.db import get_db_session
from app.schemas.audit.responses import AuditLogListResponse
from app.schemas.auth.responses import CurrentUserResponse
from app.services.audit.audit_service import AuditService

router = APIRouter(tags=["Tenant Admin"])


def get_audit_service(session: Session = Depends(get_db_session)) -> AuditService:
    """Restituisce la dependency del servizio audit."""
    return AuditService(session)


@router.get(
    "/audit-log",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Audit log tenant restituito con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo tenant admin richiesto o tenant non associato."},
    },
    summary="Elenca gli eventi di audit del tenant corrente",
)
async def get_tenant_audit_log(
    current_user: CurrentUserResponse = Depends(require_tenant_admin),
    audit_service: AuditService = Depends(get_audit_service),
) -> AuditLogListResponse:
    """Restituisce gli eventi di audit degli utenti della propria organizzazione.

    La risposta e limitata ai soli eventi prodotti da utenti appartenenti al
    tenant del chiamante.
    """
    if current_user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Il tenant admin corrente non e associato ad alcun tenant.",
        )
    return await audit_service.list_events_for_tenant(current_user.tenant_id)
