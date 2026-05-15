"""Crea lo schema security con seed iniziale."""

from datetime import UTC, datetime

import sqlalchemy as sa
from pwdlib import PasswordHash

from alembic import op

revision = "20260515_0001"
down_revision = None
branch_labels = None
depends_on = None

ADMIN_USER_ID = "6c4a6f77-7cc0-4709-a681-96b6cf724f83"
STANDARD_USER_ID = "dba4434d-99d2-4fbb-97df-a6e46e6cd6ef"


def upgrade() -> None:
    """Esegue la migrazione iniziale del modulo security."""
    op.execute("CREATE SCHEMA IF NOT EXISTS security")

    op.create_table(
        "roles",
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_roles")),
        sa.UniqueConstraint("name", name=op.f("uq_roles_name")),
        schema="security",
    )

    op.create_table(
        "permissions",
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("code", name=op.f("pk_permissions")),
        sa.UniqueConstraint("name", name=op.f("uq_permissions_name")),
        schema="security",
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role_code", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("person_id", sa.String(length=36), nullable=True),
        sa.Column("legacy_reference", sa.String(length=255), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_code"],
            ["security.roles.code"],
            name=op.f("fk_users_role_code_roles"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        schema="security",
    )
    op.create_index(
        op.f("ix_security_users_email"),
        "users",
        ["email"],
        unique=True,
        schema="security",
    )
    op.create_index(
        op.f("ix_security_users_role_code"),
        "users",
        ["role_code"],
        unique=False,
        schema="security",
    )
    op.create_index(
        op.f("ix_security_users_username"),
        "users",
        ["username"],
        unique=True,
        schema="security",
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_code", sa.String(length=50), nullable=False),
        sa.Column("permission_code", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_code"],
            ["security.permissions.code"],
            name=op.f("fk_role_permissions_permission_code_permissions"),
        ),
        sa.ForeignKeyConstraint(
            ["role_code"],
            ["security.roles.code"],
            name=op.f("fk_role_permissions_role_code_roles"),
        ),
        sa.PrimaryKeyConstraint("role_code", "permission_code", name=op.f("pk_role_permissions")),
        schema="security",
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_identifier", sa.String(length=255), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_reason", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["security.users.id"],
            name=op.f("fk_refresh_tokens_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
        schema="security",
    )
    op.create_index(
        op.f("ix_security_refresh_tokens_token_identifier"),
        "refresh_tokens",
        ["token_identifier"],
        unique=True,
        schema="security",
    )
    op.create_index(
        op.f("ix_security_refresh_tokens_user_id"),
        "refresh_tokens",
        ["user_id"],
        unique=False,
        schema="security",
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=100), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["security.users.id"],
            name=op.f("fk_audit_log_user_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_log")),
        schema="security",
    )
    op.create_index(
        op.f("ix_security_audit_log_event_type"),
        "audit_log",
        ["event_type"],
        unique=False,
        schema="security",
    )
    op.create_index(
        op.f("ix_security_audit_log_user_id"),
        "audit_log",
        ["user_id"],
        unique=False,
        schema="security",
    )

    password_hash = PasswordHash.recommended()
    now = datetime.now(UTC)

    metadata = sa.MetaData(schema="security")

    roles_table = sa.Table(
        "roles",
        metadata,
        sa.Column("code", sa.String),
        sa.Column("name", sa.String),
        sa.Column("description", sa.Text),
    )
    permissions_table = sa.Table(
        "permissions",
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

    op.bulk_insert(
        roles_table,
        [
            {
                "code": "admin",
                "name": "Amministratore",
                "description": "Ruolo amministrativo con accesso completo al backend.",
            },
            {
                "code": "user",
                "name": "Utente",
                "description": "Ruolo operativo base.",
            },
        ],
        multiinsert=False,
    )

    op.bulk_insert(
        permissions_table,
        [
            {
                "code": "users.read",
                "name": "Lettura utenti",
                "description": "Permette la lettura degli utenti applicativi.",
            },
            {
                "code": "users.write",
                "name": "Scrittura utenti",
                "description": "Permette la modifica degli utenti applicativi.",
            },
            {
                "code": "audit.read",
                "name": "Lettura audit",
                "description": "Permette la consultazione del log di audit.",
            },
        ],
        multiinsert=False,
    )

    op.bulk_insert(
        role_permissions_table,
        [
            {"role_code": "admin", "permission_code": "users.read"},
            {"role_code": "admin", "permission_code": "users.write"},
            {"role_code": "admin", "permission_code": "audit.read"},
        ],
        multiinsert=False,
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": ADMIN_USER_ID,
                "username": "admin",
                "email": "admin@example.local",
                "password_hash": password_hash.hash("admin123"),
                "role_code": "admin",
                "is_active": True,
                "person_id": None,
                "legacy_reference": None,
                "last_login_at": None,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": STANDARD_USER_ID,
                "username": "user",
                "email": "user@example.local",
                "password_hash": password_hash.hash("user123"),
                "role_code": "user",
                "is_active": True,
                "person_id": None,
                "legacy_reference": None,
                "last_login_at": None,
                "created_at": now,
                "updated_at": now,
            },
        ],
        multiinsert=False,
    )


def downgrade() -> None:
    """Esegue il rollback della migrazione iniziale del modulo security."""
    op.drop_index(
        op.f("ix_security_audit_log_user_id"),
        table_name="audit_log",
        schema="security",
    )
    op.drop_index(
        op.f("ix_security_audit_log_event_type"), table_name="audit_log", schema="security"
    )
    op.drop_table("audit_log", schema="security")

    op.drop_index(
        op.f("ix_security_refresh_tokens_user_id"),
        table_name="refresh_tokens",
        schema="security",
    )
    op.drop_index(
        op.f("ix_security_refresh_tokens_token_identifier"),
        table_name="refresh_tokens",
        schema="security",
    )
    op.drop_table("refresh_tokens", schema="security")

    op.drop_table("role_permissions", schema="security")

    op.drop_index(
        op.f("ix_security_users_username"),
        table_name="users",
        schema="security",
    )
    op.drop_index(
        op.f("ix_security_users_role_code"),
        table_name="users",
        schema="security",
    )
    op.drop_index(
        op.f("ix_security_users_email"),
        table_name="users",
        schema="security",
    )
    op.drop_table("users", schema="security")

    op.drop_table("permissions", schema="security")
    op.drop_table("roles", schema="security")
    op.execute("DROP SCHEMA IF EXISTS security")
