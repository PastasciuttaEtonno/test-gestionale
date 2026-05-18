"""Route per i costi aziendali tenant-aware."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_active_user
from app.api.deps.rbac import RequirePermission
from app.core.db import get_db_session
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.finance.requests import CreateFinanceCostRequest
from app.schemas.finance.responses import FinanceCostResponse
from app.services.finance.finance_service import FinanceService

router = APIRouter(tags=["Finance"])


def get_finance_service(session: Session = Depends(get_db_session)) -> FinanceService:
    """Restituisce il servizio applicativo finance."""
    return FinanceService(session)


@router.post(
    "/costs",
    response_model=FinanceCostResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Costo aziendale creato con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Permesso o tenant non consentiti."},
        404: {"description": "Tenant non trovato o non attivo."},
    },
    summary="Inserisce un costo aziendale tenant-aware",
)
async def create_finance_cost(
    payload: CreateFinanceCostRequest,
    current_user: CurrentUserResponse = Depends(get_active_user),
    _: CurrentUserResponse = Depends(
        RequirePermission(
            "finance.costs",
            "write",
            tenant_field_name="tenant_id",
        )
    ),
    finance_service: FinanceService = Depends(get_finance_service),
) -> FinanceCostResponse:
    """Consente l'inserimento costi solo ad admin e manager autorizzati."""
    return await finance_service.create_cost(payload=payload, current_user=current_user)
