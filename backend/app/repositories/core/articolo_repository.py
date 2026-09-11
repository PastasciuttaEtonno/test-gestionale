"""Repository per gli articoli di catalogo tenant-aware."""

from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.core.articolo import Articolo


class ArticoloRepository:
    """Accesso ai dati del modulo Articoli, sempre filtrato per tenant."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _base_query(self, tenant_id: str):
        return select(Articolo).where(Articolo.tenant_id == tenant_id)

    def list(
        self,
        tenant_id: str,
        *,
        categoria_id: str | None = None,
        is_active: bool = True,
        q: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Articolo], int]:
        """Restituisce articoli filtrati e il totale."""
        stmt = self._base_query(tenant_id).where(Articolo.is_active == is_active)
        if categoria_id:
            stmt = stmt.where(Articolo.categoria_id == categoria_id)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Articolo.codice.ilike(pattern),
                    Articolo.descrizione.ilike(pattern),
                )
            )
        total_stmt = stmt.with_only_columns(Articolo.id)
        total = len(list(self.session.scalars(total_stmt).all()))
        stmt = stmt.order_by(Articolo.codice.asc()).offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all()), total

    def get(self, tenant_id: str, articolo_id: str) -> Articolo | None:
        """Restituisce un singolo articolo del tenant."""
        stmt = self._base_query(tenant_id).where(Articolo.id == articolo_id)
        return self.session.scalar(stmt)

    # Da qui in giu', nel corpo della classe `list` e' il metodo qui sopra e non
    # il builtin: le annotazioni dei metodi seguenti usano Sequence.
    def lock_for_update(self, tenant_id: str, articolo_ids: Sequence[str]) -> Sequence[Articolo]:
        """Restituisce gli articoli indicati con lock di riga (FOR UPDATE).

        Include gli articoli disattivati: la merce gia' a documento si movimenta
        comunque. populate_existing rilegge la giacenza anche se l'articolo era
        gia' nella sessione, cosi' il valore usato e' quello sotto lock.
        """
        if not articolo_ids:
            return []
        stmt = (
            self._base_query(tenant_id)
            .where(Articolo.id.in_(articolo_ids))
            .order_by(Articolo.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return self.session.scalars(stmt).all()

    def get_by_codice(self, tenant_id: str, codice: str) -> Articolo | None:
        """Restituisce un articolo per codice nel tenant (per controllo unicita')."""
        stmt = self._base_query(tenant_id).where(Articolo.codice == codice)
        return self.session.scalar(stmt)

    def count_attivi(self, tenant_id: str) -> int:
        """Conta gli articoli attivi del tenant (per il KPI dashboard)."""
        stmt = select(func.count(Articolo.id)).where(
            Articolo.tenant_id == tenant_id,
            Articolo.is_active.is_(True),
        )
        return int(self.session.scalar(stmt) or 0)

    def create(self, articolo: Articolo) -> Articolo:
        """Persiste un nuovo articolo."""
        self.session.add(articolo)
        self.session.flush()
        self.session.refresh(articolo)
        return articolo

    def update(self, articolo: Articolo) -> Articolo:
        """Aggiorna un articolo esistente."""
        self.session.add(articolo)
        self.session.flush()
        self.session.refresh(articolo)
        return articolo
