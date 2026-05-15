"""Modello ORM delle impostazioni aziendali del tenant."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TenantCompanySettings(Base):
    """Configurazione anagrafica e documentale dell'azienda cliente."""

    __tablename__ = "tenant_company_settings"
    __table_args__ = {"schema": "core"}

    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("security.tenants.id"),
        primary_key=True,
    )
    company_name: Mapped[str] = mapped_column(String(255))
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vat_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    tax_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    legal_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    province: Mapped[str | None] = mapped_column(String(8), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    pec_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    admin_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
