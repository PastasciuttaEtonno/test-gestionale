"""Repository per le registrazioni di costi aziendali."""

from sqlalchemy.orm import Session

from app.models.core.finance_cost_entry import FinanceCostEntry


class FinanceCostRepository:
    """Repository dei costi finance tenant-aware."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def create(self, entity: FinanceCostEntry) -> FinanceCostEntry:
        """Persiste un nuovo costo aziendale."""
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity
