"""Repository per le categorie articolo tenant-aware."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.core.articolo import Articolo
from app.models.core.categoria_articolo import CategoriaArticolo


class CategoriaArticoloRepository:
    """Accesso ai dati delle categorie articolo, sempre filtrato per tenant."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _base_query(self, tenant_id: str):
        return select(CategoriaArticolo).where(CategoriaArticolo.tenant_id == tenant_id)

    def list(self, tenant_id: str, *, is_active: bool = True) -> list[CategoriaArticolo]:
        """Restituisce le categorie del tenant ordinate per nome."""
        stmt = (
            self._base_query(tenant_id)
            .where(CategoriaArticolo.is_active == is_active)
            .order_by(CategoriaArticolo.nome.asc())
        )
        return list(self.session.scalars(stmt).all())

    def get(self, tenant_id: str, categoria_id: str) -> CategoriaArticolo | None:
        """Restituisce una singola categoria del tenant."""
        stmt = self._base_query(tenant_id).where(CategoriaArticolo.id == categoria_id)
        return self.session.scalar(stmt)

    def get_by_nome(self, tenant_id: str, nome: str) -> CategoriaArticolo | None:
        """Restituisce una categoria per nome nel tenant (per controllo unicita')."""
        stmt = self._base_query(tenant_id).where(CategoriaArticolo.nome == nome)
        return self.session.scalar(stmt)

    def count_articoli_attivi(self, tenant_id: str, categoria_id: str) -> int:
        """Conta gli articoli attivi che usano la categoria nel tenant."""
        stmt = select(func.count(Articolo.id)).where(
            Articolo.tenant_id == tenant_id,
            Articolo.categoria_id == categoria_id,
            Articolo.is_active.is_(True),
        )
        return int(self.session.scalar(stmt) or 0)

    def create(self, categoria: CategoriaArticolo) -> CategoriaArticolo:
        """Persiste una nuova categoria."""
        self.session.add(categoria)
        self.session.flush()
        self.session.refresh(categoria)
        return categoria

    def update(self, categoria: CategoriaArticolo) -> CategoriaArticolo:
        """Aggiorna una categoria esistente."""
        self.session.add(categoria)
        self.session.flush()
        self.session.refresh(categoria)
        return categoria
