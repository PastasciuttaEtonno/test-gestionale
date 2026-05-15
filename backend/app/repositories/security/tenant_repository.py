"""Repository tenant."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.security.tenant import Tenant


class TenantRepository:
    """Repository per la gestione dei tenant applicativi."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def get_tenant(self, tenant_id: str) -> Tenant | None:
        """Restituisce un singolo tenant tramite identificativo."""
        statement = select(Tenant).where(Tenant.id == tenant_id)
        return self.session.scalar(statement)
