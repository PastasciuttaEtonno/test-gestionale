"""Aggiunge il ruolo tenant admin e un utente seed dedicato."""

from datetime import UTC, datetime

import sqlalchemy as sa
from pwdlib import PasswordHash

from alembic import op

revision = "20260515_0002"
down_revision = "20260515_0001"
branch_labels = None
depends_on = None

TENANT_ADMIN_USER_ID = "7e5b3f44-9856-4da0-99c7-40ef4c92b331"


def upgrade() -> None:
    """Inserisce il ruolo tenant admin nel dominio sicurezza."""
    connection = op.get_bind()
    now = datetime.now(UTC)
    password_hash = PasswordHash.recommended()
    metadata = sa.MetaData(schema="security")

    roles_table = sa.Table(
        "roles",
        metadata,
        sa.Column("code", sa.String),
        sa.Column("name", sa.String),
        sa.Column("description", sa.Text),
    )
    users_table = sa.Table(
        "users",
        metadata,
        sa.Column("id", sa.String),
        sa.Column("username", sa.String),
        sa.Column("email", sa.String),
        sa.Column("password_hash", sa.String),
        sa.Column("role_code", sa.String),
        sa.Column("is_active", sa.Boolean),
        sa.Column("person_id", sa.String),
        sa.Column("legacy_reference", sa.String),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    role_permissions_table = sa.Table(
        "role_permissions",
        metadata,
        sa.Column("role_code", sa.String),
        sa.Column("permission_code", sa.String),
    )

    role_exists = connection.execute(
        sa.text("SELECT 1 FROM security.roles WHERE code = 'tenant_admin'")
    ).scalar()
    if not role_exists:
        op.bulk_insert(
            roles_table,
            [
                {
                    "code": "tenant_admin",
                    "name": "Amministratore tenant",
                    "description": "Ruolo amministrativo per la singola azienda cliente.",
                }
            ],
            multiinsert=False,
        )

    for permission_code in ("users.read", "users.write", "audit.read"):
        permission_exists = connection.execute(
            sa.text(
                "SELECT 1 FROM security.role_permissions "
                "WHERE role_code = 'tenant_admin' AND permission_code = :permission_code"
            ),
            {"permission_code": permission_code},
        ).scalar()
        if not permission_exists:
            op.bulk_insert(
                role_permissions_table,
                [{"role_code": "tenant_admin", "permission_code": permission_code}],
                multiinsert=False,
            )

    user_exists = connection.execute(
        sa.text("SELECT 1 FROM security.users WHERE username = 'tenant.admin'")
    ).scalar()
    if not user_exists:
        op.bulk_insert(
            users_table,
            [
                {
                    "id": TENANT_ADMIN_USER_ID,
                    "username": "tenant.admin",
                    "email": "tenant.admin@example.local",
                    "password_hash": password_hash.hash("tenant123"),
                    "role_code": "tenant_admin",
                    "is_active": True,
                    "person_id": None,
                    "legacy_reference": None,
                    "last_login_at": None,
                    "created_at": now,
                    "updated_at": now,
                }
            ],
            multiinsert=False,
        )


def downgrade() -> None:
    """Rimuove ruolo e utente seed tenant admin."""
    connection = op.get_bind()

    user_exists = connection.execute(
        sa.text("SELECT 1 FROM security.users WHERE username = 'tenant.admin'")
    ).scalar()
    if user_exists:
        op.execute("DELETE FROM security.users WHERE username = 'tenant.admin'")

    op.execute("DELETE FROM security.role_permissions WHERE role_code = 'tenant_admin'")
    op.execute("DELETE FROM security.roles WHERE code = 'tenant_admin'")
