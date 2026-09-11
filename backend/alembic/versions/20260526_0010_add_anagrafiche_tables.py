"""Crea le tabelle core.anagrafiche e core.anagrafica_indirizzi con seed demo."""

from datetime import UTC, datetime

import sqlalchemy as sa

from alembic import op

revision = "20260526_0010"
down_revision = "20260526_0009"
branch_labels = None
depends_on = None

DEMO_TENANT_ID = "b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"

_ANAGRAFICHE_DEMO = [
    {
        "id": "a1000001-0000-4000-8000-000000000001",
        "tenant_id": DEMO_TENANT_ID,
        "tipo": "cliente",
        "is_persona_fisica": False,
        "ragione_sociale": "Edilceram S.r.l.",
        "cognome": None,
        "nome": None,
        "partita_iva": "03456789012",
        "codice_fiscale": "03456789012",
        "codice_sdi": "M5UXCR1",
        "pec": "edilceram@pec.it",
        "regime_fiscale": "RF01",
        "natura_giuridica": "SRL",
        "email": "amministrazione@edilceram.it",
        "telefono": "059 771234",
        "website": "www.edilceram.it",
        "note": "Cliente storico, pagamenti a 60gg.",
        "is_active": True,
    },
    {
        "id": "a1000001-0000-4000-8000-000000000002",
        "tenant_id": DEMO_TENANT_ID,
        "tipo": "cliente",
        "is_persona_fisica": False,
        "ragione_sociale": "Costruzioni Bianchi S.p.A.",
        "cognome": None,
        "nome": None,
        "partita_iva": "07654321098",
        "codice_fiscale": "07654321098",
        "codice_sdi": "K95IV18",
        "pec": "bianchi.costruzioni@legalmail.it",
        "regime_fiscale": "RF01",
        "natura_giuridica": "SPA",
        "email": "acquisti@bianchi-costruzioni.it",
        "telefono": "02 98765432",
        "website": None,
        "note": None,
        "is_active": True,
    },
    {
        "id": "a1000001-0000-4000-8000-000000000003",
        "tenant_id": DEMO_TENANT_ID,
        "tipo": "fornitore",
        "is_persona_fisica": False,
        "ragione_sociale": "Argilla & Kaolino S.r.l.",
        "cognome": None,
        "nome": None,
        "partita_iva": "02112233445",
        "codice_fiscale": "02112233445",
        "codice_sdi": "0000000",
        "pec": "argilla.kaolino@pec.it",
        "regime_fiscale": "RF01",
        "natura_giuridica": "SRL",
        "email": "ordini@argilla-kaolino.it",
        "telefono": "0522 456789",
        "website": "www.argilla-kaolino.it",
        "note": "Fornitore principale materie prime. Lead time 7gg.",
        "is_active": True,
    },
    {
        "id": "a1000001-0000-4000-8000-000000000004",
        "tenant_id": DEMO_TENANT_ID,
        "tipo": "cliente_fornitore",
        "is_persona_fisica": False,
        "ragione_sociale": "Piastrelle Nord Est S.r.l.",
        "cognome": None,
        "nome": None,
        "partita_iva": "05544332211",
        "codice_fiscale": "05544332211",
        "codice_sdi": "SUBM70N",
        "pec": "pne@pec-online.it",
        "regime_fiscale": "RF01",
        "natura_giuridica": "SRL",
        "email": "info@piastrelle-nordest.it",
        "telefono": "0444 223344",
        "website": None,
        "note": "Sia cliente per rivendita sia fornitore per semilavorati.",
        "is_active": True,
    },
    {
        "id": "a1000001-0000-4000-8000-000000000005",
        "tenant_id": DEMO_TENANT_ID,
        "tipo": "cliente",
        "is_persona_fisica": True,
        "ragione_sociale": None,
        "cognome": "Ferrari",
        "nome": "Marco",
        "partita_iva": None,
        "codice_fiscale": "FRRMRC80A01F205X",
        "codice_sdi": "0000000",
        "pec": None,
        "regime_fiscale": "RF19",
        "natura_giuridica": "DITTA_INDIVIDUALE",
        "email": "marco.ferrari@gmail.com",
        "telefono": "347 1234567",
        "website": None,
        "note": "Artigiano pavimentisti, regime forfettario.",
        "is_active": True,
    },
    {
        "id": "a1000001-0000-4000-8000-000000000006",
        "tenant_id": DEMO_TENANT_ID,
        "tipo": "fornitore",
        "is_persona_fisica": False,
        "ragione_sociale": "Trasporti Veloci S.r.l.",
        "cognome": None,
        "nome": None,
        "partita_iva": "09988776655",
        "codice_fiscale": "09988776655",
        "codice_sdi": "W7RVAP2",
        "pec": "trasportiv@pec.it",
        "regime_fiscale": "RF01",
        "natura_giuridica": "SRL",
        "email": "logistica@trasportiveloci.it",
        "telefono": "051 345678",
        "website": "www.trasportiveloci.it",
        "note": "Corriere espresso per spedizioni urgenti.",
        "is_active": True,
    },
]

_INDIRIZZI_DEMO = [
    # Edilceram — sede legale
    {
        "id": "b2000001-0000-4000-8000-000000000001",
        "anagrafica_id": "a1000001-0000-4000-8000-000000000001",
        "tipo": "legale",
        "is_principale": True,
        "indirizzo": "Via delle Ceramiche 42",
        "citta": "Sassuolo",
        "cap": "41049",
        "provincia": "MO",
        "paese": "IT",
    },
    # Argilla & Kaolino — sede legale + operativo
    {
        "id": "b2000001-0000-4000-8000-000000000002",
        "anagrafica_id": "a1000001-0000-4000-8000-000000000003",
        "tipo": "legale",
        "is_principale": True,
        "indirizzo": "Via Industriale 18",
        "citta": "Fiorano Modenese",
        "cap": "41042",
        "provincia": "MO",
        "paese": "IT",
    },
    {
        "id": "b2000001-0000-4000-8000-000000000003",
        "anagrafica_id": "a1000001-0000-4000-8000-000000000003",
        "tipo": "spedizione",
        "is_principale": False,
        "indirizzo": "Via del Magazzino 5",
        "citta": "Formigine",
        "cap": "41043",
        "provincia": "MO",
        "paese": "IT",
    },
    # Costruzioni Bianchi — sede Milano
    {
        "id": "b2000001-0000-4000-8000-000000000004",
        "anagrafica_id": "a1000001-0000-4000-8000-000000000002",
        "tipo": "legale",
        "is_principale": True,
        "indirizzo": "Corso Buenos Aires 77",
        "citta": "Milano",
        "cap": "20124",
        "provincia": "MI",
        "paese": "IT",
    },
    # Trasporti Veloci
    {
        "id": "b2000001-0000-4000-8000-000000000005",
        "anagrafica_id": "a1000001-0000-4000-8000-000000000006",
        "tipo": "legale",
        "is_principale": True,
        "indirizzo": "Via Emilia 200",
        "citta": "Bologna",
        "cap": "40139",
        "provincia": "BO",
        "paese": "IT",
    },
]


def upgrade() -> None:
    """Crea le tabelle anagrafiche e anagrafica_indirizzi con dati demo."""
    op.create_table(
        "anagrafiche",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("is_persona_fisica", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("ragione_sociale", sa.String(length=255), nullable=True),
        sa.Column("cognome", sa.String(length=150), nullable=True),
        sa.Column("nome", sa.String(length=150), nullable=True),
        sa.Column("partita_iva", sa.String(length=16), nullable=True),
        sa.Column("codice_fiscale", sa.String(length=20), nullable=True),
        sa.Column("codice_sdi", sa.String(length=7), nullable=True),
        sa.Column("pec", sa.String(length=255), nullable=True),
        sa.Column("regime_fiscale", sa.String(length=10), nullable=True),
        sa.Column("natura_giuridica", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telefono", sa.String(length=32), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_anagrafiche_tenant_id_tenants"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anagrafiche")),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_anagrafiche_tenant_id"), "anagrafiche", ["tenant_id"], schema="core"
    )
    op.create_index(op.f("ix_core_anagrafiche_tipo"), "anagrafiche", ["tipo"], schema="core")
    op.create_index(
        op.f("ix_core_anagrafiche_is_active"), "anagrafiche", ["is_active"], schema="core"
    )
    op.create_index(
        op.f("ix_core_anagrafiche_ragione_sociale"),
        "anagrafiche",
        ["ragione_sociale"],
        schema="core",
    )

    op.create_table(
        "anagrafica_indirizzi",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("anagrafica_id", sa.UUID(), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False, server_default="legale"),
        sa.Column("is_principale", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("indirizzo", sa.String(length=255), nullable=True),
        sa.Column("citta", sa.String(length=120), nullable=True),
        sa.Column("cap", sa.String(length=10), nullable=True),
        sa.Column("provincia", sa.String(length=4), nullable=True),
        sa.Column("paese", sa.String(length=2), nullable=False, server_default="IT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["anagrafica_id"],
            ["core.anagrafiche.id"],
            name=op.f("fk_anagrafica_indirizzi_anagrafica_id_anagrafiche"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_anagrafica_indirizzi")),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_anagrafica_indirizzi_anagrafica_id"),
        "anagrafica_indirizzi",
        ["anagrafica_id"],
        schema="core",
    )

    # Seed demo
    now = datetime.now(UTC)
    anagrafiche_table = sa.table(
        "anagrafiche",
        sa.column("id", sa.UUID),
        sa.column("tenant_id", sa.UUID),
        sa.column("tipo", sa.String),
        sa.column("is_persona_fisica", sa.Boolean),
        sa.column("ragione_sociale", sa.String),
        sa.column("cognome", sa.String),
        sa.column("nome", sa.String),
        sa.column("partita_iva", sa.String),
        sa.column("codice_fiscale", sa.String),
        sa.column("codice_sdi", sa.String),
        sa.column("pec", sa.String),
        sa.column("regime_fiscale", sa.String),
        sa.column("natura_giuridica", sa.String),
        sa.column("email", sa.String),
        sa.column("telefono", sa.String),
        sa.column("website", sa.String),
        sa.column("note", sa.Text),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        schema="core",
    )
    indirizzi_table = sa.table(
        "anagrafica_indirizzi",
        sa.column("id", sa.UUID),
        sa.column("anagrafica_id", sa.UUID),
        sa.column("tipo", sa.String),
        sa.column("is_principale", sa.Boolean),
        sa.column("indirizzo", sa.String),
        sa.column("citta", sa.String),
        sa.column("cap", sa.String),
        sa.column("provincia", sa.String),
        sa.column("paese", sa.String),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        schema="core",
    )
    for row in _ANAGRAFICHE_DEMO:
        op.bulk_insert(
            anagrafiche_table, [{**row, "created_at": now, "updated_at": now}], multiinsert=False
        )
    for row in _INDIRIZZI_DEMO:
        op.bulk_insert(
            indirizzi_table, [{**row, "created_at": now, "updated_at": now}], multiinsert=False
        )


def downgrade() -> None:
    """Rimuove le tabelle anagrafiche."""
    op.drop_index(
        op.f("ix_core_anagrafica_indirizzi_anagrafica_id"),
        table_name="anagrafica_indirizzi",
        schema="core",
    )
    op.drop_table("anagrafica_indirizzi", schema="core")
    op.drop_index(
        op.f("ix_core_anagrafiche_ragione_sociale"), table_name="anagrafiche", schema="core"
    )
    op.drop_index(op.f("ix_core_anagrafiche_is_active"), table_name="anagrafiche", schema="core")
    op.drop_index(op.f("ix_core_anagrafiche_tipo"), table_name="anagrafiche", schema="core")
    op.drop_index(op.f("ix_core_anagrafiche_tenant_id"), table_name="anagrafiche", schema="core")
    op.drop_table("anagrafiche", schema="core")
