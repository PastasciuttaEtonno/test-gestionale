"""Aggiunge impostazioni aziendali tenant-aware."""

from datetime import UTC, datetime

import sqlalchemy as sa

from alembic import op

revision = "20260515_0004"
down_revision = "20260515_0003"
branch_labels = None
depends_on = None

DEMO_TENANT_ID = "b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"


def upgrade() -> None:
    """Crea le tabelle di configurazione aziendale tenant-aware."""
    op.execute("CREATE SCHEMA IF NOT EXISTS core")

    op.create_table(
        "tenant_company_settings",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("vat_number", sa.String(length=32), nullable=True),
        sa.Column("tax_code", sa.String(length=32), nullable=True),
        sa.Column("legal_address", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=16), nullable=True),
        sa.Column("province", sa.String(length=8), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("pec_email", sa.String(length=255), nullable=True),
        sa.Column("admin_email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("logo_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_tenant_company_settings_tenant_id_tenants"),
        ),
        sa.PrimaryKeyConstraint("tenant_id", name=op.f("pk_tenant_company_settings")),
        schema="core",
    )

    op.create_table(
        "tenant_smtp_settings",
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("password_encrypted", sa.String(length=1024), nullable=True),
        sa.Column("sender_email", sa.String(length=255), nullable=False),
        sa.Column("sender_name", sa.String(length=255), nullable=True),
        sa.Column("use_tls", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_tenant_smtp_settings_tenant_id_tenants"),
        ),
        sa.PrimaryKeyConstraint("tenant_id", name=op.f("pk_tenant_smtp_settings")),
        schema="core",
    )

    op.create_table(
        "tenant_document_sequences",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("sequence_code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("prefix", sa.String(length=32), nullable=True),
        sa.Column("next_number", sa.Integer(), nullable=False),
        sa.Column("reset_policy", sa.String(length=32), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_tenant_document_sequences_tenant_id_tenants"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tenant_document_sequences")),
        sa.UniqueConstraint(
            "tenant_id",
            "sequence_code",
            name=op.f("uq_tenant_document_sequences_tenant_id"),
        ),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_tenant_document_sequences_tenant_id"),
        "tenant_document_sequences",
        ["tenant_id"],
        unique=False,
        schema="core",
    )

    now = datetime.now(UTC)
    metadata = sa.MetaData(schema="core")
    company_settings_table = sa.Table(
        "tenant_company_settings",
        metadata,
        sa.Column("tenant_id", sa.String),
        sa.Column("company_name", sa.String),
        sa.Column("legal_name", sa.String),
        sa.Column("vat_number", sa.String),
        sa.Column("tax_code", sa.String),
        sa.Column("legal_address", sa.String),
        sa.Column("city", sa.String),
        sa.Column("postal_code", sa.String),
        sa.Column("province", sa.String),
        sa.Column("country", sa.String),
        sa.Column("pec_email", sa.String),
        sa.Column("admin_email", sa.String),
        sa.Column("phone", sa.String),
        sa.Column("logo_url", sa.String),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    smtp_settings_table = sa.Table(
        "tenant_smtp_settings",
        metadata,
        sa.Column("tenant_id", sa.String),
        sa.Column("host", sa.String),
        sa.Column("port", sa.Integer),
        sa.Column("username", sa.String),
        sa.Column("password_encrypted", sa.String),
        sa.Column("sender_email", sa.String),
        sa.Column("sender_name", sa.String),
        sa.Column("use_tls", sa.Boolean),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    document_sequences_table = sa.Table(
        "tenant_document_sequences",
        metadata,
        sa.Column("id", sa.String),
        sa.Column("tenant_id", sa.String),
        sa.Column("sequence_code", sa.String),
        sa.Column("name", sa.String),
        sa.Column("prefix", sa.String),
        sa.Column("next_number", sa.Integer),
        sa.Column("reset_policy", sa.String),
        sa.Column("year", sa.Integer),
        sa.Column("is_active", sa.Boolean),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    op.bulk_insert(
        company_settings_table,
        [
            {
                "tenant_id": DEMO_TENANT_ID,
                "company_name": "Ceramica Demo S.r.l.",
                "legal_name": "Ceramica Demo Societa a responsabilita limitata",
                "vat_number": "IT01234567890",
                "tax_code": "01234567890",
                "legal_address": "Via delle Industrie 15",
                "city": "Sassuolo",
                "postal_code": "41049",
                "province": "MO",
                "country": "Italia",
                "pec_email": "ceramica.demo@pec.it",
                "admin_email": "amministrazione@ceramicademo.it",
                "phone": "0536 123456",
                "logo_url": "/assets/tenants/ceramica-demo/logo.svg",
                "created_at": now,
                "updated_at": now,
            }
        ],
        multiinsert=False,
    )

    op.bulk_insert(
        smtp_settings_table,
        [
            {
                "tenant_id": DEMO_TENANT_ID,
                "host": "smtp.ceramicademo.it",
                "port": 587,
                "username": "notifiche@ceramicademo.it",
                "password_encrypted": None,
                "sender_email": "notifiche@ceramicademo.it",
                "sender_name": "Ceramica Demo ERP",
                "use_tls": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
        multiinsert=False,
    )

    op.bulk_insert(
        document_sequences_table,
        [
            {
                "id": "b8df6572-1d74-458e-87e4-6365e354d2c0",
                "tenant_id": DEMO_TENANT_ID,
                "sequence_code": "invoice_electronic",
                "name": "Fattura Elettronica 2026",
                "prefix": "FE",
                "next_number": 184,
                "reset_policy": "annual",
                "year": 2026,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "545dc316-f49d-4eb7-b86e-d7d55c54ab5b",
                "tenant_id": DEMO_TENANT_ID,
                "sequence_code": "delivery_note_italy",
                "name": "Bolle Italia",
                "prefix": "BL",
                "next_number": 4441,
                "reset_policy": "continuous",
                "year": None,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": "4bb5d14f-3d92-4842-a17d-6d92bc35379a",
                "tenant_id": DEMO_TENANT_ID,
                "sequence_code": "credit_note",
                "name": "Note di credito",
                "prefix": "NC",
                "next_number": 19,
                "reset_policy": "annual",
                "year": 2026,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        ],
        multiinsert=False,
    )


def downgrade() -> None:
    """Rimuove le tabelle di configurazione aziendale tenant-aware."""
    op.drop_index(
        op.f("ix_core_tenant_document_sequences_tenant_id"),
        table_name="tenant_document_sequences",
        schema="core",
    )
    op.drop_table("tenant_document_sequences", schema="core")
    op.drop_table("tenant_smtp_settings", schema="core")
    op.drop_table("tenant_company_settings", schema="core")
