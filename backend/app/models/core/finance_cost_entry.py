"""Modello ORM dei costi aziendali tenant-aware."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FinanceCostEntry(Base):
    """Registrazione tenant-aware di un costo aziendale."""

    __tablename__ = "finance_cost_entries"
    __table_args__ = {"schema": "core"}

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(ForeignKey("security.tenants.id"), index=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("security.users.id"), index=True)
    cost_center: Mapped[str] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
