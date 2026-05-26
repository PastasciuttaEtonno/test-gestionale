"""Modello ORM degli indirizzi dell'anagrafica."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDStr


class AnagraficaIndirizzo(Base):
    """Indirizzo associato a un'anagrafica soggetto."""

    __tablename__ = "anagrafica_indirizzi"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(UUIDStr(), primary_key=True, default=lambda: str(uuid4()))
    anagrafica_id: Mapped[str] = mapped_column(
        UUIDStr(),
        ForeignKey("core.anagrafiche.id", ondelete="CASCADE"),
        index=True,
    )

    tipo: Mapped[str] = mapped_column(String(30), default="legale")
    is_principale: Mapped[bool] = mapped_column(Boolean, default=False)

    indirizzo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    citta: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cap: Mapped[str | None] = mapped_column(String(10), nullable=True)
    provincia: Mapped[str | None] = mapped_column(String(4), nullable=True)
    paese: Mapped[str] = mapped_column(String(2), default="IT")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    anagrafica: Mapped["Anagrafica"] = relationship(  # type: ignore[name-defined]
        "Anagrafica", back_populates="indirizzi"
    )
