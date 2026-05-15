"""Aggiunge persistenza per rate limiting e lockout del login."""

import sqlalchemy as sa

from alembic import op

revision = "20260515_0005"
down_revision = "20260515_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea la tabella di protezione login."""
    op.create_table(
        "login_protection",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("identifier", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_login_protection")),
        sa.UniqueConstraint(
            "identifier",
            "ip_address",
            name="uq_login_protection_identifier_ip",
        ),
        schema="security",
    )
    op.create_index(
        op.f("ix_security_login_protection_identifier"),
        "login_protection",
        ["identifier"],
        unique=False,
        schema="security",
    )
    op.create_index(
        op.f("ix_security_login_protection_ip_address"),
        "login_protection",
        ["ip_address"],
        unique=False,
        schema="security",
    )


def downgrade() -> None:
    """Rimuove la tabella di protezione login."""
    op.drop_index(
        op.f("ix_security_login_protection_ip_address"),
        table_name="login_protection",
        schema="security",
    )
    op.drop_index(
        op.f("ix_security_login_protection_identifier"),
        table_name="login_protection",
        schema="security",
    )
    op.drop_table("login_protection", schema="security")
