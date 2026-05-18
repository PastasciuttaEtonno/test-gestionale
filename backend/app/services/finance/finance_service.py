"""Servizio applicativo per costi finance tenant-aware."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core.finance_cost_entry import FinanceCostEntry
from app.models.security.tenant import Tenant
from app.repositories.core.finance_cost_repository import FinanceCostRepository
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.finance.requests import CreateFinanceCostRequest
from app.schemas.finance.responses import FinanceCostResponse


class FinanceService:
    """Casi d'uso finance tenant-aware."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.finance_cost_repository = FinanceCostRepository(session)

    async def create_cost(
        self,
        payload: CreateFinanceCostRequest,
        current_user: CurrentUserResponse,
    ) -> FinanceCostResponse:
        """Crea un nuovo costo aziendale validando il tenant target."""
        tenant_id = await self._validate_tenant_scope(payload.tenant_id.strip(), current_user)
        entity = await self.finance_cost_repository.create(
            FinanceCostEntry(
                tenant_id=tenant_id,
                created_by_user_id=current_user.id,
                cost_center=payload.cost_center,
                amount=payload.amount,
                currency=payload.currency.upper(),
                note=payload.note,
            )
        )
        self.session.commit()

        return FinanceCostResponse(
            id=entity.id,
            tenant_id=entity.tenant_id,
            cost_center=entity.cost_center,
            amount=entity.amount,
            currency=entity.currency,
            note=entity.note,
            created_at=entity.created_at,
        )

    async def _validate_tenant_scope(
        self,
        tenant_id: str,
        current_user: CurrentUserResponse,
    ) -> str:
        """Valida che il tenant target esista e sia consentito al chiamante."""
        if current_user.tenant_id is not None and current_user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant non consentito per l'utente corrente.",
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
