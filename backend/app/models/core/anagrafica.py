"""Modello ORM dell'anagrafica soggetto."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDStr

if TYPE_CHECKING:
    from app.models.core.anagrafica_indirizzo import AnagraficaIndirizzo


class Anagrafica(Base):
    """Soggetto economico tenant-aware: cliente, fornitore, agente o altro."""

    __tablename__ = "anagrafiche"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUIDStr(), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(UUIDStr(), ForeignKey("security.tenants.id"), index=True)

    tipo: Mapped[str] = mapped_column(String(30), index=True)
    is_persona_fisica: Mapped[bool] = mapped_column(Boolean, default=False)

    ragione_sociale: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    cognome: Mapped[str | None] = mapped_column(String(150), nullable=True)
    nome: Mapped[str | None] = mapped_column(String(150), nullable=True)

    partita_iva: Mapped[str | None] = mapped_column(String(16), nullable=True)
    codice_fiscale: Mapped[str | None] = mapped_column(String(20), nullable=True)
    codice_sdi: Mapped[str | None] = mapped_column(String(7), nullable=True)
    pec: Mapped[str | None] = mapped_column(String(255), nullable=True)
    regime_fiscale: Mapped[str | None] = mapped_column(String(10), nullable=True)
    natura_giuridica: Mapped[str | None] = mapped_column(String(50), nullable=True)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(32), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    indirizzi: Mapped[list["AnagraficaIndirizzo"]] = relationship(
        "AnagraficaIndirizzo", back_populates="anagrafica", cascade="all, delete-orphan"
    )
