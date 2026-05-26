"""Repository per le anagrafiche e i loro indirizzi."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.core.anagrafica import Anagrafica
from app.models.core.anagrafica_indirizzo import AnagraficaIndirizzo


class AnagraficaRepository:
    """Accesso ai dati del modulo Anagrafiche."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _base_query(self, tenant_id: str):
        return (
            select(Anagrafica)
            .where(Anagrafica.tenant_id == tenant_id)
            .options(selectinload(Anagrafica.indirizzi))
        )

    def list(
        self,
        tenant_id: str,
        *,
        tipo: str | None = None,
        is_active: bool = True,
        q: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Anagrafica], int]:
        """Restituisce anagrafiche filtrate e il totale."""
        stmt = self._base_query(tenant_id).where(Anagrafica.is_active == is_active)
        if tipo:
            stmt = stmt.where(Anagrafica.tipo == tipo)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Anagrafica.ragione_sociale.ilike(pattern),
                    Anagrafica.cognome.ilike(pattern),
                    Anagrafica.nome.ilike(pattern),
                    Anagrafica.partita_iva.ilike(pattern),
                    Anagrafica.codice_fiscale.ilike(pattern),
                )
            )
        total_stmt = stmt.with_only_columns(Anagrafica.id)
        total = len(list(self.session.scalars(total_stmt).all()))
        stmt = stmt.order_by(Anagrafica.ragione_sociale.asc(), Anagrafica.cognome.asc())
        stmt = stmt.offset(skip).limit(limit)
        return list(self.session.scalars(stmt).all()), total

    def get(self, tenant_id: str, anagrafica_id: str) -> Anagrafica | None:
        """Restituisce una singola anagrafica del tenant."""
        stmt = self._base_query(tenant_id).where(Anagrafica.id == anagrafica_id)
        return self.session.scalar(stmt)

    def create(self, anagrafica: Anagrafica) -> Anagrafica:
        """Persiste una nuova anagrafica."""
        self.session.add(anagrafica)
        self.session.flush()
        self.session.refresh(anagrafica)
        return anagrafica

    def update(self, anagrafica: Anagrafica) -> Anagrafica:
        """Aggiorna un'anagrafica esistente."""
        self.session.add(anagrafica)
        self.session.flush()
        self.session.refresh(anagrafica)
        return anagrafica

    def get_indirizzo(self, anagrafica_id: str, indirizzo_id: str) -> AnagraficaIndirizzo | None:
        """Restituisce un singolo indirizzo vincolato all'anagrafica."""
        stmt = select(AnagraficaIndirizzo).where(
            AnagraficaIndirizzo.id == indirizzo_id,
            AnagraficaIndirizzo.anagrafica_id == anagrafica_id,
        )
        return self.session.scalar(stmt)

    def create_indirizzo(self, indirizzo: AnagraficaIndirizzo) -> AnagraficaIndirizzo:
        """Persiste un nuovo indirizzo."""
        self.session.add(indirizzo)
        self.session.flush()
        self.session.refresh(indirizzo)
        return indirizzo

    def update_indirizzo(self, indirizzo: AnagraficaIndirizzo) -> AnagraficaIndirizzo:
        """Aggiorna un indirizzo esistente."""
        self.session.add(indirizzo)
        self.session.flush()
        self.session.refresh(indirizzo)
        return indirizzo

    def delete_indirizzo(self, indirizzo: AnagraficaIndirizzo) -> None:
        """Rimuove fisicamente un indirizzo."""
        self.session.delete(indirizzo)
        self.session.flush()
