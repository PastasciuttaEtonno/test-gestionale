"""Aggiunge tabella core.notifications per il Notification Center."""

import sqlalchemy as sa

from alembic import op

revision = "20260526_0007"
down_revision = "20260518_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea la tabella notifications nello schema core."""
    op.execute("CREATE SCHEMA IF NOT EXISTS core")

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("payload", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_notifications_tenant_id_tenants"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["security.users.id"],
            name=op.f("fk_notifications_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_notifications_created_at"),
        "notifications",
        ["created_at"],
        unique=False,
        schema="core",
    )
    op.create_index(
        op.f("ix_core_notifications_event_type"),
        "notifications",
        ["event_type"],
        unique=False,
        schema="core",
    )
    op.create_index(
        op.f("ix_core_notifications_is_read"),
        "notifications",
        ["is_read"],
        unique=False,
        schema="core",
    )
    op.create_index(
        op.f("ix_core_notifications_tenant_id"),
        "notifications",
        ["tenant_id"],
        unique=False,
        schema="core",
    )
    op.create_index(
        op.f("ix_core_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
        schema="core",
    )


def downgrade() -> None:
    """Rimuove la tabella notifications."""
    op.drop_index(
        op.f("ix_core_notifications_user_id"),
        table_name="notifications",
        schema="core",
    )
    op.drop_index(
        op.f("ix_core_notifications_tenant_id"),
        table_name="notifications",
        schema="core",
    )
    op.drop_index(
        op.f("ix_core_notifications_is_read"),
        table_name="notifications",
        schema="core",
    )
    op.drop_index(
        op.f("ix_core_notifications_event_type"),
        table_name="notifications",
        schema="core",
    )
    op.drop_index(
        op.f("ix_core_notifications_created_at"),
        table_name="notifications",
        schema="core",
    )
    op.drop_table("notifications", schema="core")
