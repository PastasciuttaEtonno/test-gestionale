"""Repository per le distinte base tenant-aware."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core.bom import Bom


class BomRepository:
    """Repository della distinta base."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def get_bom(self, bom_id: str) -> Bom | None:
        """Restituisce una distinta base tramite identificativo."""
        statement = select(Bom).where(Bom.id == bom_id)
        return self.session.scalar(statement)

    async def get_bom_tenant_id(self, bom_id: str) -> str | None:
        """Restituisce il tenant della distinta base richiesta."""
        statement = select(Bom.tenant_id).where(Bom.id == bom_id)
        return self.session.scalar(statement)
