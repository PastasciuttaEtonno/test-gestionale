"""Aggiunge permessi RBAC per il modulo Anagrafiche."""

import sqlalchemy as sa

from alembic import op

revision = "20260526_0009"
down_revision = "20260526_0008"
branch_labels = None
depends_on = None

_PERMISSIONS = [
    {
        "code": "anagrafiche.read",
        "name": "Lettura anagrafiche",
        "description": "Permette la consultazione delle anagrafiche tenant-aware.",
    },
    {
        "code": "anagrafiche.write",
        "name": "Scrittura anagrafiche",
        "description": "Permette la creazione e modifica delle anagrafiche tenant-aware.",
    },
    {
        "code": "anagrafiche.delete",
        "name": "Disattivazione anagrafiche",
        "description": "Permette il soft-delete delle anagrafiche tenant-aware.",
    },
]

_ROLE_PERMISSIONS = [
    ("admin", "anagrafiche.read"),
    ("admin", "anagrafiche.write"),
    ("admin", "anagrafiche.delete"),
    ("tenant_admin", "anagrafiche.read"),
    ("tenant_admin", "anagrafiche.write"),
    ("tenant_admin", "anagrafiche.delete"),
    ("manager", "anagrafiche.read"),
    ("manager", "anagrafiche.write"),
    ("worker", "anagrafiche.read"),
    ("user", "anagrafiche.read"),
]


def upgrade() -> None:
    """Inserisce i permessi anagrafiche e li assegna ai ruoli."""
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


def downgrade() -> None:
    """Rimuove i permessi anagrafiche."""
    op.execute(
        sa.text(
            "DELETE FROM security.role_permissions "
            "WHERE permission_code IN ('anagrafiche.read','anagrafiche.write','anagrafiche.delete')"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM security.permissions "
            "WHERE code IN ('anagrafiche.read','anagrafiche.write','anagrafiche.delete')"
        )
    )
