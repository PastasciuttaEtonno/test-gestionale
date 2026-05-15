"""Servizio applicativo per le impostazioni tenant admin."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security.field_encryption import FieldEncryptionService
from app.models.core.tenant_company_settings import TenantCompanySettings
from app.models.core.tenant_document_sequence import TenantDocumentSequence
from app.models.core.tenant_smtp_settings import TenantSmtpSettings
from app.repositories.core.tenant_settings_repository import TenantSettingsRepository
from app.repositories.security.tenant_repository import TenantRepository
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.tenant_admin.requests import (
    UpdateCompanySettingsRequest,
    UpdateDocumentSequenceRequest,
    UpdateSmtpSettingsRequest,
)
from app.schemas.tenant_admin.responses import (
    CompanySettingsResponse,
    DocumentSequenceListResponse,
    DocumentSequenceResponse,
    SmtpSettingsResponse,
)


class TenantSettingsService:
    """Casi d'uso tenant-aware per la console del tenant admin."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.tenant_repository = TenantRepository(session)
        self.tenant_settings_repository = TenantSettingsRepository(session)
        self.field_encryption_service = FieldEncryptionService()

    async def get_company_settings(
        self,
        current_user: CurrentUserResponse,
    ) -> CompanySettingsResponse:
        """Restituisce le impostazioni aziendali del tenant corrente."""
        tenant = await self._get_current_tenant(current_user)
        settings = await self.tenant_settings_repository.get_company_settings(tenant.id)
        if settings is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Impostazioni aziendali del tenant non trovate.",
            )
        return self._to_company_response(settings)

    async def update_company_settings(
        self,
        payload: UpdateCompanySettingsRequest,
        current_user: CurrentUserResponse,
    ) -> CompanySettingsResponse:
        """Aggiorna le impostazioni anagrafiche e documentali del tenant corrente."""
        tenant = await self._get_current_tenant(current_user)
        entity = await self.tenant_settings_repository.get_company_settings(tenant.id)
        if entity is None:
            entity = TenantCompanySettings(tenant_id=tenant.id, company_name=payload.company_name)

        entity.company_name = payload.company_name
        entity.legal_name = payload.legal_name
        entity.vat_number = payload.vat_number
        entity.tax_code = payload.tax_code
        entity.legal_address = payload.legal_address
        entity.city = payload.city
        entity.postal_code = payload.postal_code
        entity.province = payload.province
        entity.country = payload.country
        entity.pec_email = payload.pec_email
        entity.admin_email = payload.admin_email
        entity.phone = payload.phone
        entity.logo_url = payload.logo_url

        saved = await self.tenant_settings_repository.upsert_company_settings(entity)
        self.session.commit()
        return self._to_company_response(saved)

    async def get_smtp_settings(
        self,
        current_user: CurrentUserResponse,
    ) -> SmtpSettingsResponse:
        """Restituisce la configurazione SMTP del tenant corrente."""
        tenant = await self._get_current_tenant(current_user)
        settings = await self.tenant_settings_repository.get_smtp_settings(tenant.id)
        if settings is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configurazione SMTP del tenant non trovata.",
            )
        return self._to_smtp_response(settings)

    async def update_smtp_settings(
        self,
        payload: UpdateSmtpSettingsRequest,
        current_user: CurrentUserResponse,
    ) -> SmtpSettingsResponse:
        """Aggiorna la configurazione SMTP del tenant corrente."""
        tenant = await self._get_current_tenant(current_user)
        entity = await self.tenant_settings_repository.get_smtp_settings(tenant.id)
        if entity is None:
            entity = TenantSmtpSettings(
                tenant_id=tenant.id,
                host=payload.host,
                port=payload.port,
                sender_email=payload.sender_email,
            )

        entity.host = payload.host
        entity.port = payload.port
        entity.username = payload.username
        entity.sender_email = payload.sender_email
        entity.sender_name = payload.sender_name
        entity.use_tls = payload.use_tls
        if payload.password is not None:
            entity.password_encrypted = self.field_encryption_service.encrypt(payload.password)

        saved = await self.tenant_settings_repository.upsert_smtp_settings(entity)
        self.session.commit()
        return self._to_smtp_response(saved)

    async def list_document_sequences(
        self,
        current_user: CurrentUserResponse,
    ) -> DocumentSequenceListResponse:
        """Restituisce le numerazioni documentali del tenant corrente."""
        tenant = await self._get_current_tenant(current_user)
        items = await self.tenant_settings_repository.list_document_sequences(tenant.id)
        responses = [self._to_sequence_response(item) for item in items]
        return DocumentSequenceListResponse(items=responses, total=len(responses))

    async def update_document_sequence(
        self,
        sequence_code: str,
        payload: UpdateDocumentSequenceRequest,
        current_user: CurrentUserResponse,
    ) -> DocumentSequenceResponse:
        """Aggiorna una numerazione documentale del tenant corrente."""
        tenant = await self._get_current_tenant(current_user)
        entity = await self.tenant_settings_repository.get_document_sequence(
            tenant_id=tenant.id,
            sequence_code=sequence_code,
        )
        if entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Numerazione documentale non trovata per il tenant corrente.",
            )

        entity.name = payload.name
        entity.prefix = payload.prefix
        entity.next_number = payload.next_number
        entity.reset_policy = payload.reset_policy
        entity.year = payload.year
        entity.is_active = payload.is_active

        saved = await self.tenant_settings_repository.upsert_document_sequence(entity)
        self.session.commit()
        return self._to_sequence_response(saved)

    async def _get_current_tenant(self, current_user: CurrentUserResponse):
        """Risolve e valida il tenant associato all'utente corrente."""
        if current_user.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="L'utente corrente non e associato ad alcun tenant.",
            )
        tenant = await self.tenant_repository.get_tenant(current_user.tenant_id)
        if tenant is None or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant corrente non trovato o non attivo.",
            )
        return tenant

    def _to_company_response(self, entity: TenantCompanySettings) -> CompanySettingsResponse:
        """Converte il modello ORM aziendale nel payload di risposta."""
        return CompanySettingsResponse(
            tenant_id=entity.tenant_id,
            company_name=entity.company_name,
            legal_name=entity.legal_name,
            vat_number=entity.vat_number,
            tax_code=entity.tax_code,
            legal_address=entity.legal_address,
            city=entity.city,
            postal_code=entity.postal_code,
            province=entity.province,
            country=entity.country,
            pec_email=entity.pec_email,
            admin_email=entity.admin_email,
            phone=entity.phone,
            logo_url=entity.logo_url,
            updated_at=entity.updated_at,
        )

    def _to_smtp_response(self, entity: TenantSmtpSettings) -> SmtpSettingsResponse:
        """Converte il modello ORM SMTP nel payload di risposta."""
        return SmtpSettingsResponse(
            tenant_id=entity.tenant_id,
            host=entity.host,
            port=entity.port,
            username=entity.username,
            sender_email=entity.sender_email,
            sender_name=entity.sender_name,
            use_tls=entity.use_tls,
            password_configured=entity.password_encrypted is not None,
            updated_at=entity.updated_at,
        )

    def _to_sequence_response(
        self,
        entity: TenantDocumentSequence,
    ) -> DocumentSequenceResponse:
        """Converte il modello ORM numerazione nel payload di risposta."""
        return DocumentSequenceResponse(
            id=entity.id,
            tenant_id=entity.tenant_id,
            sequence_code=entity.sequence_code,
            name=entity.name,
            prefix=entity.prefix,
            next_number=entity.next_number,
            reset_policy=entity.reset_policy,
            year=entity.year,
            is_active=entity.is_active,
            updated_at=entity.updated_at,
        )
