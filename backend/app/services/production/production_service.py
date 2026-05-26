"""Servizio demo per mutazioni produzione con invalidazione cache Redis."""

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.cache import (
    build_tenant_dashboard_kpis_cache_key,
    invalidate_cache_key_best_effort,
)
from app.core.security.request_context import SecurityRequestContext
from app.domain.security.enums import AuditEventType, RoleCode
from app.models.security.audit_log import AuditLog
from app.models.security.tenant import Tenant
from app.repositories.security.audit_repository import AuditRepository
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.events.sse import EventTypes
from app.schemas.production.requests import ProductionUpdateRequest
from app.schemas.production.responses import ProductionUpdateResponse
from app.services.events.event_publisher import EventPublisher


class ProductionService:
    """Registra una mutazione produzione demo e invalida la cache KPI del tenant."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit_repository = AuditRepository(session)

    async def update_production_status(
        self,
        payload: ProductionUpdateRequest,
        current_user: CurrentUserResponse,
        request_context: SecurityRequestContext,
        redis_client: Redis,
        event_publisher: EventPublisher | None = None,
    ) -> ProductionUpdateResponse:
        """Simula una mutazione produzione persistendo audit, pulendo la cache KPI
        e notificando i client connessi via SSE."""
        tenant_id = await self._validate_tenant_scope(payload.tenant_id.strip(), current_user)

        await self.audit_repository.log_event(
            AuditLog(
                user_id=current_user.id,
                event_type=AuditEventType.PRODUCTION_ORDER_UPDATED.value,
                resource_type="production_order",
                resource_id=payload.order_code,
                payload_json={
                    "tenant_id": tenant_id,
                    "order_code": payload.order_code,
                    "status": payload.status,
                },
                ip_address=request_context.ip_address,
                user_agent=request_context.user_agent,
            )
        )
        self.session.commit()

        cache_key = build_tenant_dashboard_kpis_cache_key(tenant_id)
        await invalidate_cache_key_best_effort(redis_client, cache_key)

        if event_publisher:
            await event_publisher.publish_to_tenant(
                tenant_id,
                EventTypes.KPI_UPDATED,
                {"tenant_id": tenant_id, "reason": "production_update"},
            )

        return ProductionUpdateResponse(
            tenant_id=tenant_id,
            invalidated_cache_key=cache_key,
        )

    async def _validate_tenant_scope(
        self,
        tenant_id: str,
        current_user: CurrentUserResponse,
    ) -> str:
        """Valida accesso e tenant bersaglio dell'operazione di produzione."""
        if current_user.role_code != RoleCode.ADMIN.value and current_user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utente corrente non puo modificare dati di un altro tenant.",
            )

        tenant = self.session.scalar(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.is_active.is_(True),
            )
        )
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant non trovato o non attivo.",
            )
        return tenant.id
