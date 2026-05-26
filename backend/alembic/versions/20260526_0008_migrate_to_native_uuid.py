"""Migra tutte le colonne UUID da VARCHAR(36) al tipo nativo PostgreSQL uuid."""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "20260526_0008"
down_revision = "20260526_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Converte le colonne id e FK UUID da VARCHAR(36) al tipo nativo uuid."""
    # Step 1 — rimuovi tutti i FK che coinvolgono colonne UUID
    op.drop_constraint("fk_users_tenant_id_tenants", "users", schema="security", type_="foreignkey")
    op.drop_constraint("fk_refresh_tokens_user_id_users", "refresh_tokens", schema="security", type_="foreignkey")
    op.drop_constraint("fk_audit_log_user_id_users", "audit_log", schema="security", type_="foreignkey")
    op.drop_constraint("fk_tenant_company_settings_tenant_id_tenants", "tenant_company_settings", schema="core", type_="foreignkey")
    op.drop_constraint("fk_tenant_smtp_settings_tenant_id_tenants", "tenant_smtp_settings", schema="core", type_="foreignkey")
    op.drop_constraint("fk_tenant_document_sequences_tenant_id_tenants", "tenant_document_sequences", schema="core", type_="foreignkey")
    op.drop_constraint("fk_boms_tenant_id_tenants", "boms", schema="core", type_="foreignkey")
    op.drop_constraint("fk_finance_cost_entries_tenant_id_tenants", "finance_cost_entries", schema="core", type_="foreignkey")
    op.drop_constraint("fk_finance_cost_entries_created_by_user_id_users", "finance_cost_entries", schema="core", type_="foreignkey")
    op.drop_constraint("fk_notifications_user_id_users", "notifications", schema="core", type_="foreignkey")
    op.drop_constraint("fk_notifications_tenant_id_tenants", "notifications", schema="core", type_="foreignkey")

    # Step 2 — altera le colonne PK (security.tenants.id e security.users.id)
    op.execute(sa.text("ALTER TABLE security.tenants ALTER COLUMN id TYPE uuid USING id::uuid"))
    op.execute(sa.text("ALTER TABLE security.users ALTER COLUMN id TYPE uuid USING id::uuid"))

    # Step 3 — altera le colonne FK che dipendono da tenants.id o users.id
    op.execute(sa.text("ALTER TABLE security.users ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid"))
    op.execute(sa.text("ALTER TABLE security.refresh_tokens ALTER COLUMN id TYPE uuid USING id::uuid"))
    op.execute(sa.text("ALTER TABLE security.refresh_tokens ALTER COLUMN user_id TYPE uuid USING user_id::uuid"))
    op.execute(sa.text("ALTER TABLE security.audit_log ALTER COLUMN id TYPE uuid USING id::uuid"))
    op.execute(sa.text("ALTER TABLE security.audit_log ALTER COLUMN user_id TYPE uuid USING user_id::uuid"))
    op.execute(sa.text("ALTER TABLE security.login_protection ALTER COLUMN id TYPE uuid USING id::uuid"))
    op.execute(sa.text("ALTER TABLE core.tenant_company_settings ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid"))
    op.execute(sa.text("ALTER TABLE core.tenant_smtp_settings ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid"))
    op.execute(sa.text("ALTER TABLE core.tenant_document_sequences ALTER COLUMN id TYPE uuid USING id::uuid"))
    op.execute(sa.text("ALTER TABLE core.tenant_document_sequences ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid"))
    op.execute(sa.text("ALTER TABLE core.boms ALTER COLUMN id TYPE uuid USING id::uuid"))
    op.execute(sa.text("ALTER TABLE core.boms ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid"))
    op.execute(sa.text("ALTER TABLE core.finance_cost_entries ALTER COLUMN id TYPE uuid USING id::uuid"))
    op.execute(sa.text("ALTER TABLE core.finance_cost_entries ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid"))
    op.execute(sa.text("ALTER TABLE core.finance_cost_entries ALTER COLUMN created_by_user_id TYPE uuid USING created_by_user_id::uuid"))
    op.execute(sa.text("ALTER TABLE core.notifications ALTER COLUMN id TYPE uuid USING id::uuid"))
    op.execute(sa.text("ALTER TABLE core.notifications ALTER COLUMN user_id TYPE uuid USING user_id::uuid"))
    op.execute(sa.text("ALTER TABLE core.notifications ALTER COLUMN tenant_id TYPE uuid USING tenant_id::uuid"))

    # Step 4 — ricrea i FK con le colonne ora di tipo uuid
    op.create_foreign_key(
        "fk_users_tenant_id_tenants",
        "users", "tenants",
        ["tenant_id"], ["id"],
        source_schema="security", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_refresh_tokens_user_id_users",
        "refresh_tokens", "users",
        ["user_id"], ["id"],
        source_schema="security", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_audit_log_user_id_users",
        "audit_log", "users",
        ["user_id"], ["id"],
        source_schema="security", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_tenant_company_settings_tenant_id_tenants",
        "tenant_company_settings", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_tenant_smtp_settings_tenant_id_tenants",
        "tenant_smtp_settings", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_tenant_document_sequences_tenant_id_tenants",
        "tenant_document_sequences", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_boms_tenant_id_tenants",
        "boms", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_finance_cost_entries_tenant_id_tenants",
        "finance_cost_entries", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_finance_cost_entries_created_by_user_id_users",
        "finance_cost_entries", "users",
        ["created_by_user_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_notifications_user_id_users",
        "notifications", "users",
        ["user_id"], ["id"],
        source_schema="core", referent_schema="security",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_notifications_tenant_id_tenants",
        "notifications", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Ritorna le colonne UUID da tipo nativo uuid a VARCHAR(36)."""
    op.drop_constraint("fk_users_tenant_id_tenants", "users", schema="security", type_="foreignkey")
    op.drop_constraint("fk_refresh_tokens_user_id_users", "refresh_tokens", schema="security", type_="foreignkey")
    op.drop_constraint("fk_audit_log_user_id_users", "audit_log", schema="security", type_="foreignkey")
    op.drop_constraint("fk_tenant_company_settings_tenant_id_tenants", "tenant_company_settings", schema="core", type_="foreignkey")
    op.drop_constraint("fk_tenant_smtp_settings_tenant_id_tenants", "tenant_smtp_settings", schema="core", type_="foreignkey")
    op.drop_constraint("fk_tenant_document_sequences_tenant_id_tenants", "tenant_document_sequences", schema="core", type_="foreignkey")
    op.drop_constraint("fk_boms_tenant_id_tenants", "boms", schema="core", type_="foreignkey")
    op.drop_constraint("fk_finance_cost_entries_tenant_id_tenants", "finance_cost_entries", schema="core", type_="foreignkey")
    op.drop_constraint("fk_finance_cost_entries_created_by_user_id_users", "finance_cost_entries", schema="core", type_="foreignkey")
    op.drop_constraint("fk_notifications_user_id_users", "notifications", schema="core", type_="foreignkey")
    op.drop_constraint("fk_notifications_tenant_id_tenants", "notifications", schema="core", type_="foreignkey")

    op.execute(sa.text("ALTER TABLE security.tenants ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE security.users ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE security.users ALTER COLUMN tenant_id TYPE varchar(36) USING tenant_id::text"))
    op.execute(sa.text("ALTER TABLE security.refresh_tokens ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE security.refresh_tokens ALTER COLUMN user_id TYPE varchar(36) USING user_id::text"))
    op.execute(sa.text("ALTER TABLE security.audit_log ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE security.audit_log ALTER COLUMN user_id TYPE varchar(36) USING user_id::text"))
    op.execute(sa.text("ALTER TABLE security.login_protection ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE core.tenant_company_settings ALTER COLUMN tenant_id TYPE varchar(36) USING tenant_id::text"))
    op.execute(sa.text("ALTER TABLE core.tenant_smtp_settings ALTER COLUMN tenant_id TYPE varchar(36) USING tenant_id::text"))
    op.execute(sa.text("ALTER TABLE core.tenant_document_sequences ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE core.tenant_document_sequences ALTER COLUMN tenant_id TYPE varchar(36) USING tenant_id::text"))
    op.execute(sa.text("ALTER TABLE core.boms ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE core.boms ALTER COLUMN tenant_id TYPE varchar(36) USING tenant_id::text"))
    op.execute(sa.text("ALTER TABLE core.finance_cost_entries ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE core.finance_cost_entries ALTER COLUMN tenant_id TYPE varchar(36) USING tenant_id::text"))
    op.execute(sa.text("ALTER TABLE core.finance_cost_entries ALTER COLUMN created_by_user_id TYPE varchar(36) USING created_by_user_id::text"))
    op.execute(sa.text("ALTER TABLE core.notifications ALTER COLUMN id TYPE varchar(36) USING id::text"))
    op.execute(sa.text("ALTER TABLE core.notifications ALTER COLUMN user_id TYPE varchar(36) USING user_id::text"))
    op.execute(sa.text("ALTER TABLE core.notifications ALTER COLUMN tenant_id TYPE varchar(36) USING tenant_id::text"))

    op.create_foreign_key(
        "fk_users_tenant_id_tenants",
        "users", "tenants",
        ["tenant_id"], ["id"],
        source_schema="security", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_refresh_tokens_user_id_users",
        "refresh_tokens", "users",
        ["user_id"], ["id"],
        source_schema="security", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_audit_log_user_id_users",
        "audit_log", "users",
        ["user_id"], ["id"],
        source_schema="security", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_tenant_company_settings_tenant_id_tenants",
        "tenant_company_settings", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_tenant_smtp_settings_tenant_id_tenants",
        "tenant_smtp_settings", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_tenant_document_sequences_tenant_id_tenants",
        "tenant_document_sequences", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_boms_tenant_id_tenants",
        "boms", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_finance_cost_entries_tenant_id_tenants",
        "finance_cost_entries", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_finance_cost_entries_created_by_user_id_users",
        "finance_cost_entries", "users",
        ["created_by_user_id"], ["id"],
        source_schema="core", referent_schema="security",
    )
    op.create_foreign_key(
        "fk_notifications_user_id_users",
        "notifications", "users",
        ["user_id"], ["id"],
        source_schema="core", referent_schema="security",
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_notifications_tenant_id_tenants",
        "notifications", "tenants",
        ["tenant_id"], ["id"],
        source_schema="core", referent_schema="security",
        ondelete="CASCADE",
    )
