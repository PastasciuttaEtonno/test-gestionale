"""Route demo produzione con invalidazione cache dashboard."""

from fastapi import APIRouter, Depends, Request, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.api.deps.auth import get_active_user
from app.core.db import get_db_session
from app.core.redis import get_redis_client
from app.core.security.request_context import build_security_request_context
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.production.requests import ProductionUpdateRequest
from app.schemas.production.responses import ProductionUpdateResponse
from app.services.production.production_service import ProductionService

router = APIRouter(tags=["Production"])


def get_production_service(session: Session = Depends(get_db_session)) -> ProductionService:
    """Restituisce il servizio demo del dominio produzione."""
    return ProductionService(session)


@router.put(
    "/update",
    response_model=ProductionUpdateResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Aggiornamento produzione completato e cache invalidata."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Tenant non consentito per l'utente corrente."},
        404: {"description": "Tenant non trovato o non attivo."},
    },
    summary="Aggiorna uno stato produzione e invalida la cache KPI del tenant",
)
async def update_production(
    payload: ProductionUpdateRequest,
    request: Request,
    current_user: CurrentUserResponse = Depends(get_active_user),
    redis_client: Redis = Depends(get_redis_client),
    production_service: ProductionService = Depends(get_production_service),
) -> ProductionUpdateResponse:
    """Simula una mutazione produzione persistita e invalida i KPI cacheati del tenant."""
    return await production_service.update_production_status(
        payload=payload,
        current_user=current_user,
        request_context=build_security_request_context(request),
        redis_client=redis_client,
    )
