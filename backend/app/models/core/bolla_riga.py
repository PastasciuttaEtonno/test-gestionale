"""Modello ORM della riga di una bolla / DDT."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDStr

if TYPE_CHECKING:
    from app.models.core.bolla import Bolla


class BollaRiga(Base):
    """Riga di una bolla con snapshot immutabile dei dati articolo."""

    __tablename__ = "bolle_righe"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUIDStr(), primary_key=True, default=lambda: str(uuid4()))
    bolla_id: Mapped[str] = mapped_column(
        UUIDStr(), ForeignKey("core.bolle.id", ondelete="CASCADE"), index=True
    )
    articolo_id: Mapped[str | None] = mapped_column(
        UUIDStr(), ForeignKey("core.articoli.id"), nullable=True
    )

    # Snapshot dei dati articolo al momento dell'inserimento (immutabile).
    codice_articolo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descrizione: Mapped[str] = mapped_column(String(255))
    unita_misura: Mapped[str] = mapped_column(String(10), default="pz")
    quantita: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0"))
    prezzo_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))
    aliquota_iva: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("22"))
    importo_riga: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    ordine: Mapped[int] = mapped_column(Integer, default=0)

    bolla: Mapped["Bolla"] = relationship("Bolla", back_populates="righe")
