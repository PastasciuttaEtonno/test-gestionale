"""Modello ORM delle numerazioni documentali del tenant."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TenantDocumentSequence(Base):
    """Numerazione documentale configurabile per tenant."""

    __tablename__ = "tenant_document_sequences"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(ForeignKey("security.tenants.id"), index=True)
    sequence_code: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(255))
    prefix: Mapped[str | None] = mapped_column(String(32), nullable=True)
    next_number: Mapped[int] = mapped_column(Integer)
    reset_policy: Mapped[str] = mapped_column(String(32))
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
