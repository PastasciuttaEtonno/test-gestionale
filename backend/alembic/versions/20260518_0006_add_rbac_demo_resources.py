"""Aggiunge ruoli RBAC estesi, permessi e risorse demo tenant-aware."""

from datetime import UTC, datetime

import sqlalchemy as sa
from pwdlib import PasswordHash

from alembic import op

revision = "20260518_0006"
down_revision = "20260515_0005"
branch_labels = None
depends_on = None

DEMO_TENANT_ID = "b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"
MANAGER_USER_ID = "34e978f4-33c8-45ae-b6cb-314e32e83aa1"
WORKER_USER_ID = "81c1b0e0-d146-4d4c-aa89-b18d9de14936"
BOM_DEMO_ID = "c4c2b9df-cf80-4938-a1ea-369862bd6bd6"


def upgrade() -> None:
    """Crea tabelle demo RBAC e aggiorna il catalogo ruoli/permessi."""
    op.create_table(
        "boms",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_boms_tenant_id_tenants"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_boms")),
        sa.UniqueConstraint("code", name=op.f("uq_boms_code")),
        schema="core",
    )
    op.create_index(op.f("ix_core_boms_code"), "boms", ["code"], unique=True, schema="core")
    op.create_index(
        op.f("ix_core_boms_tenant_id"),
        "boms",
        ["tenant_id"],
        unique=False,
        schema="core",
    )

    op.create_table(
        "finance_cost_entries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("cost_center", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["security.users.id"],
            name=op.f("fk_finance_cost_entries_created_by_user_id_users"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_finance_cost_entries_tenant_id_tenants"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_finance_cost_entries")),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_finance_cost_entries_created_by_user_id"),
        "finance_cost_entries",
        ["created_by_user_id"],
        unique=False,
        schema="core",
    )
    op.create_index(
        op.f("ix_core_finance_cost_entries_tenant_id"),
        "finance_cost_entries",
        ["tenant_id"],
        unique=False,
        schema="core",
    )

    connection = op.get_bind()
    now = datetime.now(UTC)
    password_hash = PasswordHash.recommended()

    security_metadata = sa.MetaData(schema="security")
    core_metadata = sa.MetaData(schema="core")

    roles_table = sa.Table(
        "roles",
        security_metadata,
        sa.Column("code", sa.String),
        sa.Column("name", sa.String),
        sa.Column("description", sa.Text),
    )
    permissions_table = sa.Table(
        "permissions",
        security_metadata,
        sa.Column("code", sa.String),
        sa.Column("name", sa.String),
        sa.Column("description", sa.Text),
    )
    role_permissions_table = sa.Table(
        "role_permissions",
        security_metadata,
        sa.Column("role_code", sa.String),
        sa.Column("permission_code", sa.String),
    )
    users_table = sa.Table(
        "users",
        security_metadata,
        sa.Column("id", sa.String),
        sa.Column("username", sa.String),
        sa.Column("email", sa.String),
        sa.Column("password_hash", sa.String),
        sa.Column("role_code", sa.String),
        sa.Column("is_active", sa.Boolean),
        sa.Column("person_id", sa.String),
        sa.Column("tenant_id", sa.String),
        sa.Column("legacy_reference", sa.String),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    boms_table = sa.Table(
        "boms",
        core_metadata,
        sa.Column("id", sa.String),
        sa.Column("tenant_id", sa.String),
        sa.Column("code", sa.String),
        sa.Column("name", sa.String),
        sa.Column("description", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )

    for role in (
        {
            "code": "manager",
            "name": "Manager",
            "description": "Ruolo gestionale tenant-aware con scrittura controllata.",
        },
        {
            "code": "worker",
            "name": "Worker",
            "description": "Ruolo operativo tenant-aware con lettura di produzione.",
        },
    ):
        exists = connection.execute(
            sa.text("SELECT 1 FROM security.roles WHERE code = :code"),
            {"code": role["code"]},
        ).scalar()
        if not exists:
            op.bulk_insert(roles_table, [role], multiinsert=False)

    for permission in (
        {
            "code": "bom.read",
            "name": "Lettura distinte base",
            "description": "Permette la consultazione delle distinte base tenant-aware.",
        },
        {
            "code": "finance.costs.write",
            "name": "Scrittura costi aziendali",
            "description": "Permette l'inserimento dei costi finance tenant-aware.",
        },
        {
            "code": "bom.delete",
            "name": "Eliminazione distinte base",
            "description": "Permette l'eliminazione di una distinta base tenant-aware.",
        },
    ):
        exists = connection.execute(
            sa.text("SELECT 1 FROM security.permissions WHERE code = :code"),
            {"code": permission["code"]},
        ).scalar()
        if not exists:
            op.bulk_insert(permissions_table, [permission], multiinsert=False)

    mappings = (
        ("admin", "bom.read"),
        ("admin", "finance.costs.write"),
        ("admin", "bom.delete"),
        ("tenant_admin", "bom.read"),
        ("tenant_admin", "finance.costs.write"),
        ("tenant_admin", "bom.delete"),
        ("manager", "bom.read"),
        ("manager", "finance.costs.write"),
        ("worker", "bom.read"),
        ("user", "bom.read"),
    )
    for role_code, permission_code in mappings:
        exists = connection.execute(
            sa.text(
                "SELECT 1 FROM security.role_permissions "
                "WHERE role_code = :role_code AND permission_code = :permission_code"
            ),
            {"role_code": role_code, "permission_code": permission_code},
        ).scalar()
        if not exists:
            op.bulk_insert(
                role_permissions_table,
                [{"role_code": role_code, "permission_code": permission_code}],
                multiinsert=False,
            )

    for user in (
        {
            "id": MANAGER_USER_ID,
            "username": "manager.demo",
            "email": "manager.demo@example.local",
            "password_hash": password_hash.hash("manager123"),
            "role_code": "manager",
            "is_active": True,
            "person_id": None,
            "tenant_id": DEMO_TENANT_ID,
            "legacy_reference": None,
            "last_login_at": None,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": WORKER_USER_ID,
            "username": "worker.demo",
            "email": "worker.demo@example.local",
            "password_hash": password_hash.hash("worker123"),
            "role_code": "worker",
            "is_active": True,
            "person_id": None,
            "tenant_id": DEMO_TENANT_ID,
            "legacy_reference": None,
            "last_login_at": None,
            "created_at": now,
            "updated_at": now,
        },
    ):
        exists = connection.execute(
            sa.text("SELECT 1 FROM security.users WHERE username = :username"),
            {"username": user["username"]},
        ).scalar()
        if not exists:
            op.bulk_insert(users_table, [user], multiinsert=False)

    bom_exists = connection.execute(
        sa.text("SELECT 1 FROM core.boms WHERE id = :id"),
        {"id": BOM_DEMO_ID},
    ).scalar()
    if not bom_exists:
        op.bulk_insert(
            boms_table,
            [
                {
                    "id": BOM_DEMO_ID,
                    "tenant_id": DEMO_TENANT_ID,
                    "code": "BOM-2026-001",
                    "name": "Distinta Base Linea Forni",
                    "description": "Componenti e semilavorati per il ciclo forno linea A.",
                    "created_at": now,
                    "updated_at": now,
                }
            ],
            multiinsert=False,
        )


def downgrade() -> None:
    """Rimuove ruoli, permessi e risorse demo RBAC."""
    op.execute("DELETE FROM core.finance_cost_entries")
    op.execute("DELETE FROM core.boms WHERE id = 'c4c2b9df-cf80-4938-a1ea-369862bd6bd6'")
    op.execute("DELETE FROM security.users WHERE username IN ('manager.demo', 'worker.demo')")
    op.execute(
        "DELETE FROM security.role_permissions "
        "WHERE permission_code IN ('bom.read', 'finance.costs.write', 'bom.delete')"
    )
    op.execute(
        "DELETE FROM security.permissions "
        "WHERE code IN ('bom.read', 'finance.costs.write', 'bom.delete')"
    )
    op.execute("DELETE FROM security.roles WHERE code IN ('manager', 'worker')")

    op.drop_index(
        op.f("ix_core_finance_cost_entries_tenant_id"),
        table_name="finance_cost_entries",
        schema="core",
    )
    op.drop_index(
        op.f("ix_core_finance_cost_entries_created_by_user_id"),
        table_name="finance_cost_entries",
        schema="core",
    )
    op.drop_table("finance_cost_entries", schema="core")

    op.drop_index(op.f("ix_core_boms_tenant_id"), table_name="boms", schema="core")
    op.drop_index(op.f("ix_core_boms_code"), table_name="boms", schema="core")
    op.drop_table("boms", schema="core")
