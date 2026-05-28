"""Crea le tabelle core.categorie_articolo e core.articoli con permessi RBAC e seed demo."""

from datetime import UTC, datetime
from decimal import Decimal

import sqlalchemy as sa

from alembic import op

revision = "20260528_0012"
down_revision = "20260527_0011"
branch_labels = None
depends_on = None

DEMO_TENANT_ID = "b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"

_PERMISSIONS = [
    {
        "code": "articoli.read",
        "name": "Lettura articoli",
        "description": "Permette la consultazione di articoli e categorie tenant-aware.",
    },
    {
        "code": "articoli.write",
        "name": "Scrittura articoli",
        "description": "Permette la creazione e modifica di articoli e categorie tenant-aware.",
    },
    {
        "code": "articoli.delete",
        "name": "Disattivazione articoli",
        "description": "Permette il soft-delete di articoli e categorie tenant-aware.",
    },
]

_ROLE_PERMISSIONS = [
    ("admin", "articoli.read"),
    ("admin", "articoli.write"),
    ("admin", "articoli.delete"),
    ("tenant_admin", "articoli.read"),
    ("tenant_admin", "articoli.write"),
    ("tenant_admin", "articoli.delete"),
    ("manager", "articoli.read"),
    ("manager", "articoli.write"),
    ("worker", "articoli.read"),
    ("user", "articoli.read"),
]

_CATEGORIE_DEMO = [
    {
        "id": "c3000001-0000-4000-8000-000000000001",
        "tenant_id": DEMO_TENANT_ID,
        "nome": "Pavimenti",
        "descrizione": "Piastrelle e gres per pavimentazione.",
        "is_active": True,
    },
    {
        "id": "c3000001-0000-4000-8000-000000000002",
        "tenant_id": DEMO_TENANT_ID,
        "nome": "Rivestimenti",
        "descrizione": "Rivestimenti per pareti interne ed esterne.",
        "is_active": True,
    },
    {
        "id": "c3000001-0000-4000-8000-000000000003",
        "tenant_id": DEMO_TENANT_ID,
        "nome": "Accessori posa",
        "descrizione": "Colle, fughe e materiali di posa.",
        "is_active": True,
    },
]

_ARTICOLI_DEMO = [
    {
        "id": "d4000001-0000-4000-8000-000000000001",
        "tenant_id": DEMO_TENANT_ID,
        "codice": "PAV-GRES-6060-GR",
        "categoria_id": "c3000001-0000-4000-8000-000000000001",
        "descrizione": "Gres porcellanato 60x60 grigio effetto cemento",
        "unita_misura": "m²",
        "prezzo_unitario": Decimal("18.5000"),
        "aliquota_iva": Decimal("22.00"),
        "giacenza": Decimal("420.000"),
        "codice_ean": "8001234500011",
        "note": "Rettificato, spessore 9mm.",
        "is_active": True,
        "version": 1,
    },
    {
        "id": "d4000001-0000-4000-8000-000000000002",
        "tenant_id": DEMO_TENANT_ID,
        "codice": "PAV-GRES-6060-BE",
        "categoria_id": "c3000001-0000-4000-8000-000000000001",
        "descrizione": "Gres porcellanato 60x60 beige effetto pietra",
        "unita_misura": "m²",
        "prezzo_unitario": Decimal("19.9000"),
        "aliquota_iva": Decimal("22.00"),
        "giacenza": Decimal("310.500"),
        "codice_ean": "8001234500028",
        "note": None,
        "is_active": True,
        "version": 1,
    },
    {
        "id": "d4000001-0000-4000-8000-000000000003",
        "tenant_id": DEMO_TENANT_ID,
        "codice": "RIV-MOS-3030-BL",
        "categoria_id": "c3000001-0000-4000-8000-000000000002",
        "descrizione": "Mosaico vetroso 30x30 blu per rivestimento",
        "unita_misura": "m²",
        "prezzo_unitario": Decimal("34.0000"),
        "aliquota_iva": Decimal("22.00"),
        "giacenza": Decimal("85.000"),
        "codice_ean": "8001234500035",
        "note": "Adatto a bagni e piscine.",
        "is_active": True,
        "version": 1,
    },
    {
        "id": "d4000001-0000-4000-8000-000000000004",
        "tenant_id": DEMO_TENANT_ID,
        "codice": "RIV-CER-2540-BI",
        "categoria_id": "c3000001-0000-4000-8000-000000000002",
        "descrizione": "Ceramica rivestimento 25x40 bianco lucido",
        "unita_misura": "m²",
        "prezzo_unitario": Decimal("12.7500"),
        "aliquota_iva": Decimal("22.00"),
        "giacenza": Decimal("540.000"),
        "codice_ean": "8001234500042",
        "note": None,
        "is_active": True,
        "version": 1,
    },
    {
        "id": "d4000001-0000-4000-8000-000000000005",
        "tenant_id": DEMO_TENANT_ID,
        "codice": "ACC-COLLA-C2-25",
        "categoria_id": "c3000001-0000-4000-8000-000000000003",
        "descrizione": "Colla cementizia C2TE sacco 25kg",
        "unita_misura": "scatola",
        "prezzo_unitario": Decimal("14.2000"),
        "aliquota_iva": Decimal("22.00"),
        "giacenza": Decimal("260.000"),
        "codice_ean": "8001234500059",
        "note": "Bancale da 48 sacchi.",
        "is_active": True,
        "version": 1,
    },
    {
        "id": "d4000001-0000-4000-8000-000000000006",
        "tenant_id": DEMO_TENANT_ID,
        "codice": "ACC-FUGA-GR-5",
        "categoria_id": "c3000001-0000-4000-8000-000000000003",
        "descrizione": "Fugante grigio cemento secchio 5kg",
        "unita_misura": "pz",
        "prezzo_unitario": Decimal("8.9000"),
        "aliquota_iva": Decimal("22.00"),
        "giacenza": Decimal("150.000"),
        "codice_ean": "8001234500066",
        "note": None,
        "is_active": True,
        "version": 1,
    },
]


def upgrade() -> None:
    """Crea categorie e articoli, inserisce i permessi RBAC e popola il seed demo."""
    op.create_table(
        "categorie_articolo",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descrizione", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_categorie_articolo_tenant_id_tenants"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categorie_articolo")),
        sa.UniqueConstraint("tenant_id", "nome", name=op.f("uq_categorie_articolo_tenant_nome")),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_categorie_articolo_tenant_id"),
        "categorie_articolo",
        ["tenant_id"],
        schema="core",
    )

    op.create_table(
        "articoli",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("codice", sa.String(length=50), nullable=False),
        sa.Column("categoria_id", sa.UUID(), nullable=True),
        sa.Column("descrizione", sa.String(length=255), nullable=False),
        sa.Column("unita_misura", sa.String(length=10), nullable=False, server_default="pz"),
        sa.Column(
            "prezzo_unitario", sa.Numeric(precision=12, scale=4), nullable=False, server_default="0"
        ),
        sa.Column(
            "aliquota_iva", sa.Numeric(precision=5, scale=2), nullable=False, server_default="22"
        ),
        sa.Column(
            "giacenza", sa.Numeric(precision=12, scale=3), nullable=False, server_default="0"
        ),
        sa.Column("codice_ean", sa.String(length=14), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["security.tenants.id"],
            name=op.f("fk_articoli_tenant_id_tenants"),
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["core.categorie_articolo.id"],
            name=op.f("fk_articoli_categoria_id_categorie_articolo"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_articoli")),
        sa.UniqueConstraint("tenant_id", "codice", name=op.f("uq_articoli_tenant_codice")),
        schema="core",
    )
    op.create_index(op.f("ix_core_articoli_tenant_id"), "articoli", ["tenant_id"], schema="core")
    op.create_index(
        op.f("ix_core_articoli_categoria_id"), "articoli", ["categoria_id"], schema="core"
    )
    op.create_index(op.f("ix_core_articoli_is_active"), "articoli", ["is_active"], schema="core")

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
    categorie_table = sa.table(
        "categorie_articolo",
        sa.column("id", sa.UUID),
        sa.column("tenant_id", sa.UUID),
        sa.column("nome", sa.String),
        sa.column("descrizione", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        schema="core",
    )
    articoli_table = sa.table(
        "articoli",
        sa.column("id", sa.UUID),
        sa.column("tenant_id", sa.UUID),
        sa.column("codice", sa.String),
        sa.column("categoria_id", sa.UUID),
        sa.column("descrizione", sa.String),
        sa.column("unita_misura", sa.String),
        sa.column("prezzo_unitario", sa.Numeric),
        sa.column("aliquota_iva", sa.Numeric),
        sa.column("giacenza", sa.Numeric),
        sa.column("codice_ean", sa.String),
        sa.column("note", sa.Text),
        sa.column("is_active", sa.Boolean),
        sa.column("version", sa.Integer),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
        schema="core",
    )
    for row in _CATEGORIE_DEMO:
        op.bulk_insert(
            categorie_table, [{**row, "created_at": now, "updated_at": now}], multiinsert=False
        )
    for row in _ARTICOLI_DEMO:
        op.bulk_insert(
            articoli_table, [{**row, "created_at": now, "updated_at": now}], multiinsert=False
        )


def downgrade() -> None:
    """Rimuove articoli, categorie e i relativi permessi RBAC."""
    op.execute(
        sa.text(
            "DELETE FROM security.role_permissions "
            "WHERE permission_code IN ('articoli.read','articoli.write','articoli.delete')"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM security.permissions "
            "WHERE code IN ('articoli.read','articoli.write','articoli.delete')"
        )
    )
    op.drop_index(op.f("ix_core_articoli_is_active"), table_name="articoli", schema="core")
    op.drop_index(op.f("ix_core_articoli_categoria_id"), table_name="articoli", schema="core")
    op.drop_index(op.f("ix_core_articoli_tenant_id"), table_name="articoli", schema="core")
    op.drop_table("articoli", schema="core")
    op.drop_index(
        op.f("ix_core_categorie_articolo_tenant_id"), table_name="categorie_articolo", schema="core"
    )
    op.drop_table("categorie_articolo", schema="core")
