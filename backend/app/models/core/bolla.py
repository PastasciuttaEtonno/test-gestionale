"""Modello ORM della bolla / DDT tenant-aware."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDStr

if TYPE_CHECKING:
    from app.models.core.bolla_riga import BollaRiga


class Bolla(Base):
    """Documento di trasporto (DDT) tenant-aware con testata e righe."""

    __tablename__ = "bolle"
    __table_args__ = (
        UniqueConstraint("tenant_id", "numero", name="uq_bolle_tenant_numero"),
        {"schema": "core"},
    )

    id: Mapped[str] = mapped_column(UUIDStr(), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(UUIDStr(), ForeignKey("security.tenants.id"), index=True)

    numero: Mapped[str | None] = mapped_column(String(40), nullable=True)
    anno: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stato: Mapped[str] = mapped_column(String(20), default="bozza", index=True)
    data_documento: Mapped[date] = mapped_column(Date)
    anagrafica_id: Mapped[str] = mapped_column(
        UUIDStr(), ForeignKey("core.anagrafiche.id"), index=True
    )

    causale_trasporto: Mapped[str] = mapped_column(String(50), default="vendita")
    aspetto_beni: Mapped[str | None] = mapped_column(String(60), nullable=True)
    num_colli: Mapped[int | None] = mapped_column(Integer, nullable=True)
    peso_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    trasporto_a_cura: Mapped[str | None] = mapped_column(String(20), nullable=True)
    vettore: Mapped[str | None] = mapped_column(String(120), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    totale_imponibile: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    totale_iva: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    totale: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    righe: Mapped[list["BollaRiga"]] = relationship(
        "BollaRiga",
        back_populates="bolla",
        cascade="all, delete-orphan",
        order_by="BollaRiga.ordine",
    )
