"""Repository delle configurazioni tenant-aware."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core.tenant_company_settings import TenantCompanySettings
from app.models.core.tenant_document_sequence import TenantDocumentSequence
from app.models.core.tenant_smtp_settings import TenantSmtpSettings


class TenantSettingsRepository:
    """Repository per le impostazioni aziendali del tenant."""

    def __init__(self, session: Session) -> None:
        self.session = session

    async def get_company_settings(self, tenant_id: str) -> TenantCompanySettings | None:
        """Restituisce le impostazioni anagrafiche del tenant."""
        statement = select(TenantCompanySettings).where(
            TenantCompanySettings.tenant_id == tenant_id
        )
        return self.session.scalar(statement)

    async def upsert_company_settings(
        self,
        entity: TenantCompanySettings,
    ) -> TenantCompanySettings:
        """Crea o aggiorna le impostazioni anagrafiche del tenant."""
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    async def get_smtp_settings(self, tenant_id: str) -> TenantSmtpSettings | None:
        """Restituisce la configurazione SMTP del tenant."""
        statement = select(TenantSmtpSettings).where(TenantSmtpSettings.tenant_id == tenant_id)
        return self.session.scalar(statement)

    async def upsert_smtp_settings(self, entity: TenantSmtpSettings) -> TenantSmtpSettings:
        """Crea o aggiorna la configurazione SMTP del tenant."""
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    async def list_document_sequences(self, tenant_id: str) -> list[TenantDocumentSequence]:
        """Restituisce le numerazioni documentali del tenant."""
        statement = (
            select(TenantDocumentSequence)
            .where(TenantDocumentSequence.tenant_id == tenant_id)
            .order_by(TenantDocumentSequence.sequence_code.asc())
        )
        return list(self.session.scalars(statement).all())

    async def get_document_sequence(
        self,
        tenant_id: str,
        sequence_code: str,
    ) -> TenantDocumentSequence | None:
        """Restituisce una singola numerazione documentale per codice."""
        statement = select(TenantDocumentSequence).where(
            TenantDocumentSequence.tenant_id == tenant_id,
            TenantDocumentSequence.sequence_code == sequence_code,
        )
        return self.session.scalar(statement)

    async def upsert_document_sequence(
        self,
        entity: TenantDocumentSequence,
    ) -> TenantDocumentSequence:
        """Crea o aggiorna una numerazione documentale del tenant."""
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity
