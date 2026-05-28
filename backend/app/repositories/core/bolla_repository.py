"""Repository per le bolle / DDT tenant-aware."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.core.bolla import Bolla
from app.models.core.tenant_document_sequence import TenantDocumentSequence


class BollaRepository:
    """Accesso ai dati del modulo Bolle, sempre filtrato per tenant."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _base_query(self, tenant_id: str):
        return select(Bolla).where(Bolla.tenant_id == tenant_id).options(selectinload(Bolla.righe))

    def list(
        self,
        tenant_id: str,
        *,
        stato: str | None = None,
        anagrafica_id: str | None = None,
        q: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Bolla], int]:
        """Restituisce bolle filtrate e il totale."""
        stmt = self._base_query(tenant_id)
        if stato:
            stmt = stmt.where(Bolla.stato == stato)
        if anagrafica_id:
            stmt = stmt.where(Bolla.anagrafica_id == anagrafica_id)
        if q:
            stmt = stmt.where(Bolla.numero.ilike(f"%{q}%"))
        total_stmt = stmt.with_only_columns(Bolla.id)
        total = len(list(self.session.scalars(total_stmt).all()))
        stmt = stmt.order_by(Bolla.created_at.desc()).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all()), total

    def get(self, tenant_id: str, bolla_id: str) -> Bolla | None:
        """Restituisce una singola bolla del tenant con le righe."""
        stmt = self._base_query(tenant_id).where(Bolla.id == bolla_id)
        return self.session.scalar(stmt)

    def create(self, bolla: Bolla) -> Bolla:
        """Persiste una nuova bolla (e le sue righe)."""
        self.session.add(bolla)
        self.session.flush()
        self.session.refresh(bolla)
        return bolla

    def update(self, bolla: Bolla) -> Bolla:
        """Aggiorna una bolla esistente."""
        self.session.add(bolla)
        self.session.flush()
        self.session.refresh(bolla)
        return bolla

    def delete(self, bolla: Bolla) -> None:
        """Rimuove fisicamente una bolla (usato solo per le bozze)."""
        self.session.delete(bolla)
        self.session.flush()

    def count_emesse_nel_mese(self, tenant_id: str) -> int:
        """Conta le bolle emesse del tenant nel mese corrente (per il KPI)."""
        now = datetime.now(UTC)
        inizio_mese = datetime(now.year, now.month, 1, tzinfo=UTC)
        stmt = select(func.count(Bolla.id)).where(
            Bolla.tenant_id == tenant_id,
            Bolla.stato == "emessa",
            Bolla.created_at >= inizio_mese,
        )
        return int(self.session.scalar(stmt) or 0)

    def lock_document_sequence(
        self, tenant_id: str, sequence_code: str
    ) -> TenantDocumentSequence | None:
        """Restituisce la sequence con lock di riga (FOR UPDATE) per numerazione safe.

        Il lock serializza le emissioni concorrenti evitando numeri duplicati.
        """
        stmt = (
            select(TenantDocumentSequence)
            .where(
                TenantDocumentSequence.tenant_id == tenant_id,
                TenantDocumentSequence.sequence_code == sequence_code,
            )
            .with_for_update()
        )
        return self.session.scalar(stmt)
