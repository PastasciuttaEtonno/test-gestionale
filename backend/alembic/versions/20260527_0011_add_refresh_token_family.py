"""Aggiunge campi famiglia ai refresh token per reuse detection e absolute timeout."""

import sqlalchemy as sa

from alembic import op

revision = "20260527_0011"
down_revision = "20260526_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Aggiunge family_id, parent_token_identifier e family_created_at a security.refresh_tokens.

    Backfill: ogni token esistente diventa una famiglia di se' stesso (family_id = id).
    Cosi' tutti i refresh token vecchi continuano a ruotare senza essere considerati orfani.
    """
    op.add_column(
        "refresh_tokens",
        sa.Column("family_id", sa.dialects.postgresql.UUID(as_uuid=False), nullable=True),
        schema="security",
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("parent_token_identifier", sa.String(length=255), nullable=True),
        schema="security",
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("family_created_at", sa.DateTime(timezone=True), nullable=True),
        schema="security",
    )

    # Backfill: ogni token esistente diventa la propria famiglia di 1.
    op.execute(
        """
        UPDATE security.refresh_tokens
        SET family_id = id,
            family_created_at = issued_at
        WHERE family_id IS NULL
        """
    )

    op.alter_column(
        "refresh_tokens",
        "family_id",
        nullable=False,
        schema="security",
    )
    op.alter_column(
        "refresh_tokens",
        "family_created_at",
        nullable=False,
        schema="security",
    )
    op.create_index(
        "ix_refresh_tokens_family_id",
        "refresh_tokens",
        ["family_id"],
        schema="security",
    )


def downgrade() -> None:
    """Rimuove i campi famiglia introdotti dalla migration 0011."""
    op.drop_index("ix_refresh_tokens_family_id", table_name="refresh_tokens", schema="security")
    op.drop_column("refresh_tokens", "family_created_at", schema="security")
    op.drop_column("refresh_tokens", "parent_token_identifier", schema="security")
    op.drop_column("refresh_tokens", "family_id", schema="security")
