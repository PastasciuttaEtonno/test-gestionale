"""Route amministrative."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin
from app.core.db import get_db_session
from app.schemas.audit.responses import AuditLogListResponse
from app.schemas.auth.responses import CurrentUserResponse
from app.services.audit.audit_service import AuditService

router = APIRouter(tags=["Admin"])


def get_audit_service(session: Session = Depends(get_db_session)) -> AuditService:
    """Restituisce la dependency del servizio audit."""
    return AuditService(session)


@router.get(
    "/audit-log",
    response_model=AuditLogListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Audit log restituito con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo admin richiesto."},
    },
    summary="Elenca gli eventi di audit",
)
async def get_audit_log(
    _: CurrentUserResponse = Depends(require_admin),
    audit_service: AuditService = Depends(get_audit_service),
) -> AuditLogListResponse:
    """Restituisce gli eventi di audit per consultazione amministrativa.

    L'accesso e riservato agli amministratori perche i dati di audit sono
    sensibili dal punto di vista della sicurezza e rilevanti operativamente.
    """
    return await audit_service.list_events()
