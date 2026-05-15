"""Introduce tenant e scoping utenti di livello 2."""

from datetime import UTC, datetime

import sqlalchemy as sa

from alembic import op

revision = "20260515_0003"
down_revision = "20260515_0002"
branch_labels = None
depends_on = None

DEMO_TENANT_ID = "b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"


def upgrade() -> None:
    """Crea il dominio tenant e collega gli utenti all'organizzazione."""
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tenants")),
        sa.UniqueConstraint("code", name=op.f("uq_tenants_code")),
        sa.UniqueConstraint("name", name=op.f("uq_tenants_name")),
        schema="security",
    )
    op.create_index(
        op.f("ix_security_tenants_code"),
        "tenants",
        ["code"],
        unique=True,
        schema="security",
    )

    op.add_column(
        "users",
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        schema="security",
    )
    op.create_index(
        op.f("ix_security_users_tenant_id"),
        "users",
        ["tenant_id"],
        unique=False,
        schema="security",
    )
    op.create_foreign_key(
        op.f("fk_users_tenant_id_tenants"),
        "users",
        "tenants",
        ["tenant_id"],
        ["id"],
        source_schema="security",
        referent_schema="security",
    )

    now = datetime.now(UTC)
    metadata = sa.MetaData(schema="security")
    tenants_table = sa.Table(
        "tenants",
        metadata,
        sa.Column("id", sa.String),
        sa.Column("code", sa.String),
        sa.Column("name", sa.String),
        sa.Column("is_active", sa.Boolean),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.bulk_insert(
        tenants_table,
        [
            {
                "id": DEMO_TENANT_ID,
                "code": "ceramica-demo",
                "name": "Ceramica Demo S.r.l.",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ],
        multiinsert=False,
    )

    op.execute(
        sa.text(
            "UPDATE security.users "
            "SET tenant_id = :tenant_id "
            "WHERE username IN ('tenant.admin', 'user')"
        ).bindparams(tenant_id=DEMO_TENANT_ID)
    )


def downgrade() -> None:
    """Rimuove il dominio tenant e il collegamento utenti-organizzazione."""
    op.execute(sa.text("UPDATE security.users SET tenant_id = NULL"))
    op.drop_constraint(
        op.f("fk_users_tenant_id_tenants"),
        "users",
        schema="security",
        type_="foreignkey",
    )
    op.drop_index(op.f("ix_security_users_tenant_id"), table_name="users", schema="security")
    op.drop_column("users", "tenant_id", schema="security")
    op.drop_index(op.f("ix_security_tenants_code"), table_name="tenants", schema="security")
    op.drop_table("tenants", schema="security")
