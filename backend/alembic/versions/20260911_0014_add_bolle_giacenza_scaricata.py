"""Aggiunge a core.bolle il flag giacenza_scaricata.

Da questa versione l'emissione scarica la giacenza e l'annullamento la rimette.
Le bolle emesse prima non l'hanno mai scaricata: partono con il flag a false,
cosi' annullarle non rimette in magazzino merce che non era mai stata tolta.
"""

import sqlalchemy as sa

from alembic import op

revision = "20260911_0014"
down_revision = "20260529_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Aggiunge la colonna, a false per tutte le bolle gia' presenti."""
    op.add_column(
        "bolle",
        sa.Column("giacenza_scaricata", sa.Boolean(), nullable=False, server_default=sa.false()),
        schema="core",
    )


def downgrade() -> None:
    """Rimuove la colonna."""
    op.drop_column("bolle", "giacenza_scaricata", schema="core")
