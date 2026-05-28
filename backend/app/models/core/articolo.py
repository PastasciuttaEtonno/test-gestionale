"""Modello ORM dell'articolo di catalogo tenant-aware."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDStr


class Articolo(Base):
    """Articolo di catalogo tenant-aware: prodotto o materiale a listino."""

    __tablename__ = "articoli"
    __table_args__ = (
        UniqueConstraint("tenant_id", "codice", name="uq_articoli_tenant_codice"),
        {"schema": "core"},
    )

    id: Mapped[str] = mapped_column(UUIDStr(), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(UUIDStr(), ForeignKey("security.tenants.id"), index=True)

    codice: Mapped[str] = mapped_column(String(50))
    categoria_id: Mapped[str | None] = mapped_column(
        UUIDStr(), ForeignKey("core.categorie_articolo.id"), nullable=True, index=True
    )
    descrizione: Mapped[str] = mapped_column(String(255))
    unita_misura: Mapped[str] = mapped_column(String(10), default="pz")
    prezzo_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0"))
    aliquota_iva: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("22"))
    giacenza: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("0"))
    codice_ean: Mapped[str | None] = mapped_column(String(14), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
