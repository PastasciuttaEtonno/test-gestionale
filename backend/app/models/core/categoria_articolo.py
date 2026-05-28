"""Modello ORM della categoria articolo tenant-aware."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDStr


class CategoriaArticolo(Base):
    """Categoria di classificazione degli articoli, isolata per tenant."""

    __tablename__ = "categorie_articolo"
    __table_args__ = (
        UniqueConstraint("tenant_id", "nome", name="uq_categorie_articolo_tenant_nome"),
        {"schema": "core"},
    )

    id: Mapped[str] = mapped_column(UUIDStr(), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(UUIDStr(), ForeignKey("security.tenants.id"), index=True)

    nome: Mapped[str] = mapped_column(String(100))
    descrizione: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
