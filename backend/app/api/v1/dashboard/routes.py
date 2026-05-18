"""Route dashboard con cache Redis e rate limiting."""

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.api.deps.auth import get_active_user
from app.core.config import settings
from app.core.db import get_db_session
from app.core.rate_limit import rate_limit_dependency
from app.core.redis import get_redis_client
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.dashboard.responses import DashboardKpisResponse
from app.services.dashboard.dashboard_service import DashboardService

router = APIRouter(tags=["Dashboard"])


def get_dashboard_service(session: Session = Depends(get_db_session)) -> DashboardService:
    """Restituisce il servizio KPI della dashboard tenant-aware."""
    return DashboardService(session)


@router.get(
    "/kpis",
    response_model=DashboardKpisResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "KPI dashboard restituiti con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Utente non associato a un tenant valido."},
        429: {"description": "Rate limit superato."},
    },
    summary="Restituisce i KPI dashboard tenant-aware con cache Redis",
)
async def get_dashboard_kpis(
    _: None = Depends(
        rate_limit_dependency(
            limit=settings.api_rate_limit_requests_per_minute,
            window_seconds=60,
            scope="dashboard-kpis",
        )
    ),
    current_user: CurrentUserResponse = Depends(get_active_user),
    redis_client: Redis = Depends(get_redis_client),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardKpisResponse:
    """Restituisce i KPI della dashboard usando cache Redis isolata per tenant."""
    return await dashboard_service.get_dashboard_kpis(current_user, redis_client)
