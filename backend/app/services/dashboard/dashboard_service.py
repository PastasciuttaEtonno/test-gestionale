"""Servizi applicativi per KPI dashboard tenant-aware con cache Redis."""

from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.cache import build_tenant_dashboard_kpis_cache_key, get_or_set_model_cache
from app.core.config import settings
from app.models.core.articolo import Articolo
from app.models.core.tenant_company_settings import TenantCompanySettings
from app.models.core.tenant_smtp_settings import TenantSmtpSettings
from app.models.security.audit_log import AuditLog
from app.models.security.tenant import Tenant
from app.models.security.user import User
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.dashboard.responses import DashboardKpisResponse


class DashboardService:
    """Costruisce e memorizza in cache i KPI dashboard isolati per tenant."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def get_dashboard_kpis(
        self,
        current_user: CurrentUserResponse,
        redis_client: Redis,
    ) -> DashboardKpisResponse:
        """Restituisce i KPI tenant-aware usando cache Redis con TTL."""
        tenant_id = await self._resolve_tenant_id(current_user)
        cache_key = build_tenant_dashboard_kpis_cache_key(tenant_id)
        return await get_or_set_model_cache(
            redis_client=redis_client,
            key=cache_key,
            ttl_seconds=settings.dashboard_kpi_cache_ttl_seconds,
            model_class=DashboardKpisResponse,
            loader=lambda: self._load_dashboard_kpis(tenant_id),
        )

    async def _load_dashboard_kpis(self, tenant_id: str) -> DashboardKpisResponse:
        """Carica i KPI dal database in caso di cache miss."""
        total_users = self.session.scalar(
            select(func.count(User.id)).where(User.tenant_id == tenant_id)
        )
        active_users = self.session.scalar(
            select(func.count(User.id)).where(
                User.tenant_id == tenant_id,
                User.is_active.is_(True),
            )
        )
        audit_events_last_24h = self.session.scalar(
            select(func.count(AuditLog.id))
            .join(User, User.id == AuditLog.user_id)
            .where(
                User.tenant_id == tenant_id,
                AuditLog.created_at >= datetime.now(UTC) - timedelta(hours=24),
            )
        )
        company_profile_configured = self.session.scalar(
            select(func.count(TenantCompanySettings.tenant_id)).where(
                TenantCompanySettings.tenant_id == tenant_id
            )
        )
        smtp_configured = self.session.scalar(
            select(func.count(TenantSmtpSettings.tenant_id)).where(
                TenantSmtpSettings.tenant_id == tenant_id
            )
        )
        total_articoli = self.session.scalar(
            select(func.count(Articolo.id)).where(
                Articolo.tenant_id == tenant_id,
                Articolo.is_active.is_(True),
            )
        )

        return DashboardKpisResponse(
            tenant_id=tenant_id,
            total_users=int(total_users or 0),
            active_users=int(active_users or 0),
            audit_events_last_24h=int(audit_events_last_24h or 0),
            total_articoli=int(total_articoli or 0),
            company_profile_configured=bool(company_profile_configured),
            smtp_configured=bool(smtp_configured),
            generated_at=datetime.now(UTC),
        )

    async def _resolve_tenant_id(self, current_user: CurrentUserResponse) -> str:
        """Valida e restituisce il tenant corrente per utenti tenant-scoped."""
        if current_user.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utente corrente non e associato ad alcun tenant.",
            )

        tenant = self.session.scalar(
            select(Tenant).where(
                Tenant.id == current_user.tenant_id,
                Tenant.is_active.is_(True),
            )
        )
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant corrente non trovato o non attivo.",
            )
        return tenant.id
