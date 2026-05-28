"""Crea le tabelle core.bolle e core.bolle_righe con permessi RBAC e seed demo."""

from datetime import UTC, date, datetime
from decimal import Decimal

import sqlalchemy as sa

from alembic import op

revision = "20260529_0013"
down_revision = "20260528_0012"
branch_labels = None
depends_on = None

DEMO_TENANT_ID = "b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"

# Anagrafiche e articoli gia' seedati nelle migration precedenti.
ANAGRAFICA_EDILCERAM = "a1000001-0000-4000-8000-000000000001"
ANAGRAFICA_BIANCHI = "a1000001-0000-4000-8000-000000000002"
ART_GRES_GR = "d4000001-0000-4000-8000-000000000001"
ART_MOSAICO = "d4000001-0000-4000-8000-000000000003"
ART_COLLA = "d4000001-0000-4000-8000-000000000005"

_PERMISSIONS = [
    {
        "code": "bolle.read",
        "name": "Lettura bolle",
        "description": "Permette la consultazione delle bolle/DDT tenant-aware.",
    },
    {
        "code": "bolle.write",
        "name": "Scrittura ed emissione bolle",
        "description": "Permette creazione/modifica bozze, gestione righe ed emissione bolle.",
    },
    {
        "code": "bolle.delete",
        "name": "Cancellazione e annullamento bolle",
        "description": "Permette la cancellazione delle bozze e l'annullamento delle bolle emesse.",
    },
]

_ROLE_PERMISSIONS = [
    ("admin", "bolle.read"),
    ("admin", "bolle.write"),
    ("admin", "bolle.delete"),
    ("tenant_admin", "bolle.read"),
    ("tenant_admin", "bolle.write"),
    ("tenant_admin", "bolle.delete"),
    ("manager", "bolle.read"),
    ("manager", "bolle.write"),
    ("worker", "bolle.read"),
    ("user", "bolle.read"),
]

BOLLA_EMESSA = "e5000001-0000-4000-8000-000000000001"
BOLLA_BOZZA = "e5000001-0000-4000-8000-000000000002"


def upgrade() -> None:
    """Crea bolle e righe, inserisce i permessi RBAC e popola il seed demo."""
    op.create_table(
        "bolle",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("numero", sa.String(length=40), nullable=True),
        sa.Column("anno", sa.Integer(), nullable=True),
        sa.Column("stato", sa.String(length=20), nullable=False, server_default="bozza"),
        sa.Column("data_documento", sa.Date(), nullable=False),
        sa.Column("anagrafica_id", sa.UUID(), nullable=False),
        sa.Column(
            "causale_trasporto", sa.String(length=50), nullable=False, server_default="vendita"
        ),
        sa.Column("aspetto_beni", sa.String(length=60), nullable=True),
        sa.Column("num_colli", sa.Integer(), nullable=True),
        sa.Column("peso_kg", sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column("trasporto_a_cura", sa.String(length=20), nullable=True),
        sa.Column("vettore", sa.String(length=120), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "totale_imponibile",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "totale_iva", sa.Numeric(precision=14, scale=2), nullable=False, server_default="0"
        ),
        sa.Column("totale", sa.Numeric(precision=14, scale=2), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["security.tenants.id"], name=op.f("fk_bolle_tenant_id_tenants")
        ),
        sa.ForeignKeyConstraint(
            ["anagrafica_id"],
            ["core.anagrafiche.id"],
            name=op.f("fk_bolle_anagrafica_id_anagrafiche"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bolle")),
        sa.UniqueConstraint("tenant_id", "numero", name=op.f("uq_bolle_tenant_numero")),
        schema="core",
    )
    op.create_index(op.f("ix_core_bolle_tenant_id"), "bolle", ["tenant_id"], schema="core")
    op.create_index(op.f("ix_core_bolle_stato"), "bolle", ["stato"], schema="core")
    op.create_index(op.f("ix_core_bolle_anagrafica_id"), "bolle", ["anagrafica_id"], schema="core")

    op.create_table(
        "bolle_righe",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("bolla_id", sa.UUID(), nullable=False),
        sa.Column("articolo_id", sa.UUID(), nullable=True),
        sa.Column("codice_articolo", sa.String(length=50), nullable=True),
        sa.Column("descrizione", sa.String(length=255), nullable=False),
        sa.Column("unita_misura", sa.String(length=10), nullable=False, server_default="pz"),
        sa.Column(
            "quantita", sa.Numeric(precision=12, scale=3), nullable=False, server_default="0"
        ),
        sa.Column(
            "prezzo_unitario", sa.Numeric(precision=12, scale=4), nullable=False, server_default="0"
        ),
        sa.Column(
            "aliquota_iva", sa.Numeric(precision=5, scale=2), nullable=False, server_default="22"
        ),
        sa.Column(
            "importo_riga", sa.Numeric(precision=14, scale=2), nullable=False, server_default="0"
        ),
        sa.Column("ordine", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["bolla_id"],
            ["core.bolle.id"],
            name=op.f("fk_bolle_righe_bolla_id_bolle"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["articolo_id"],
            ["core.articoli.id"],
            name=op.f("fk_bolle_righe_articolo_id_articoli"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bolle_righe")),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_bolle_righe_bolla_id"), "bolle_righe", ["bolla_id"], schema="core"
    )

    # Permessi RBAC
    connection = op.get_bind()
    permissions_table = sa.table(
        "permissions",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        schema="security",
    )
    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("role_code", sa.String),
        sa.column("permission_code", sa.String),
        schema="security",
    )
    for perm in _PERMISSIONS:
        exists = connection.execute(
            sa.text("SELECT 1 FROM security.permissions WHERE code = :code"),
            {"code": perm["code"]},
        ).scalar()
        if not exists:
            connection.execute(permissions_table.insert().values(**perm))
    for role_code, permission_code in _ROLE_PERMISSIONS:
        exists = connection.execute(
            sa.text(
                "SELECT 1 FROM security.role_permissions "
                "WHERE role_code = :rc AND permission_code = :pc"
            ),
            {"rc": role_code, "pc": permission_code},
        ).scalar()
        if not exists:
            connection.execute(
                role_permissions_table.insert().values(
                    role_code=role_code, permission_code=permission_code
                )
            )

    # Seed demo
    now = datetime.now(UTC)
    bolle_table = sa.table(
        "bolle",
        sa.column("id", sa.UUID),
        sa.column("tenant_id", sa.UUID),
        sa.column("numero", sa.String),
        sa.column("anno", sa.Integer),
        sa.column("stato", sa.String),
        sa.column("data_documento", sa.Date),
        sa.column("anagrafica_id", sa.UUID),
        sa.column("causale_trasporto", sa.String),
        sa.column("aspetto_beni", sa.String),
        sa.column("num_colli", sa.Integer),
        sa.column("peso_kg", sa.Numeric),
        sa.column("trasporto_a_cura", sa.String),
        sa.column("vettore", sa.String),
        sa.column("note", sa.Text),
        sa.column("totale_imponibile", sa.Numeric),
        sa.column("totale_iva", sa.Numeric),
        sa.column("totale", sa.Numeric),
        sa.column("is_active", sa.Boolean),
        sa.column("version", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        schema="core",
    )
    righe_table = sa.table(
        "bolle_righe",
        sa.column("id", sa.UUID),
        sa.column("bolla_id", sa.UUID),
        sa.column("articolo_id", sa.UUID),
        sa.column("codice_articolo", sa.String),
        sa.column("descrizione", sa.String),
        sa.column("unita_misura", sa.String),
        sa.column("quantita", sa.Numeric),
        sa.column("prezzo_unitario", sa.Numeric),
        sa.column("aliquota_iva", sa.Numeric),
        sa.column("importo_riga", sa.Numeric),
        sa.column("ordine", sa.Integer),
        schema="core",
    )

    op.bulk_insert(
        bolle_table,
        [
            {
                "id": BOLLA_EMESSA,
                "tenant_id": DEMO_TENANT_ID,
                "numero": "BL4441",
                "anno": 2026,
                "stato": "emessa",
                "data_documento": date(2026, 5, 20),
                "anagrafica_id": ANAGRAFICA_EDILCERAM,
                "causale_trasporto": "vendita",
                "aspetto_beni": "Pallet",
                "num_colli": 3,
                "peso_kg": Decimal("520.000"),
                "trasporto_a_cura": "destinatario",
                "vettore": "Trasporti Veloci S.r.l.",
                "note": "Consegna piano terra, scarico a cura del cliente.",
                "totale_imponibile": Decimal("1067.00"),
                "totale_iva": Decimal("234.74"),
                "totale": Decimal("1301.74"),
                "is_active": True,
                "version": 1,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": BOLLA_BOZZA,
                "tenant_id": DEMO_TENANT_ID,
                "numero": None,
                "anno": None,
                "stato": "bozza",
                "data_documento": date(2026, 5, 28),
                "anagrafica_id": ANAGRAFICA_BIANCHI,
                "causale_trasporto": "vendita",
                "aspetto_beni": "Scatole",
                "num_colli": None,
                "peso_kg": None,
                "trasporto_a_cura": "mittente",
                "vettore": None,
                "note": None,
                "totale_imponibile": Decimal("680.00"),
                "totale_iva": Decimal("149.60"),
                "totale": Decimal("829.60"),
                "is_active": True,
                "version": 1,
                "created_at": now,
                "updated_at": now,
            },
        ],
        multiinsert=False,
    )

    op.bulk_insert(
        righe_table,
        [
            {
                "id": "f6000001-0000-4000-8000-000000000001",
                "bolla_id": BOLLA_EMESSA,
                "articolo_id": ART_GRES_GR,
                "codice_articolo": "PAV-GRES-6060-GR",
                "descrizione": "Gres porcellanato 60x60 grigio effetto cemento",
                "unita_misura": "m²",
                "quantita": Decimal("50.000"),
                "prezzo_unitario": Decimal("18.5000"),
                "aliquota_iva": Decimal("22.00"),
                "importo_riga": Decimal("925.00"),
                "ordine": 1,
            },
            {
                "id": "f6000001-0000-4000-8000-000000000002",
                "bolla_id": BOLLA_EMESSA,
                "articolo_id": ART_COLLA,
                "codice_articolo": "ACC-COLLA-C2-25",
                "descrizione": "Colla cementizia C2TE sacco 25kg",
                "unita_misura": "scatola",
                "quantita": Decimal("10.000"),
                "prezzo_unitario": Decimal("14.2000"),
                "aliquota_iva": Decimal("22.00"),
                "importo_riga": Decimal("142.00"),
                "ordine": 2,
            },
            {
                "id": "f6000001-0000-4000-8000-000000000003",
                "bolla_id": BOLLA_BOZZA,
                "articolo_id": ART_MOSAICO,
                "codice_articolo": "RIV-MOS-3030-BL",
                "descrizione": "Mosaico vetroso 30x30 blu per rivestimento",
                "unita_misura": "m²",
                "quantita": Decimal("20.000"),
                "prezzo_unitario": Decimal("34.0000"),
                "aliquota_iva": Decimal("22.00"),
                "importo_riga": Decimal("680.00"),
                "ordine": 1,
            },
        ],
        multiinsert=False,
    )

    # La sequence DDT parte da 4441 (seed migration 0004). La bolla emessa nel seed
    # consuma 4441, quindi la portiamo a 4442 per la prossima emissione runtime.
    connection.execute(
        sa.text(
            "UPDATE core.tenant_document_sequences "
            "SET next_number = 4442 "
            "WHERE tenant_id = :tid AND sequence_code = 'delivery_note_italy' "
            "AND next_number = 4441"
        ),
        {"tid": DEMO_TENANT_ID},
    )


def downgrade() -> None:
    """Rimuove bolle, righe e i relativi permessi RBAC."""
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE core.tenant_document_sequences "
            "SET next_number = 4441 "
            "WHERE tenant_id = :tid AND sequence_code = 'delivery_note_italy' "
            "AND next_number = 4442"
        ),
        {"tid": DEMO_TENANT_ID},
    )
    op.execute(
        sa.text(
            "DELETE FROM security.role_permissions "
            "WHERE permission_code IN ('bolle.read','bolle.write','bolle.delete')"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM security.permissions "
            "WHERE code IN ('bolle.read','bolle.write','bolle.delete')"
        )
    )
    op.drop_index(op.f("ix_core_bolle_righe_bolla_id"), table_name="bolle_righe", schema="core")
    op.drop_table("bolle_righe", schema="core")
    op.drop_index(op.f("ix_core_bolle_anagrafica_id"), table_name="bolle", schema="core")
    op.drop_index(op.f("ix_core_bolle_stato"), table_name="bolle", schema="core")
    op.drop_index(op.f("ix_core_bolle_tenant_id"), table_name="bolle", schema="core")
    op.drop_table("bolle", schema="core")
