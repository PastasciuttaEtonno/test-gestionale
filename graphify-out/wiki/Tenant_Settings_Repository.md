# Tenant Settings Repository

> 25 nodes · cohesion 0.11

## Key Concepts

- **TenantSettingsRepository** (29 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **str** (7 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Session** (7 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **TenantDocumentSequence** (6 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **TenantCompanySettings** (5 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **TenantSmtpSettings** (5 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **.__init__()** (5 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **.get_company_settings()** (4 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **.get_document_sequence()** (4 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **.get_smtp_settings()** (4 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **.list_document_sequences()** (4 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **.upsert_company_settings()** (3 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **.upsert_document_sequence()** (3 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **.upsert_smtp_settings()** (3 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **tenant_settings_repository.py** (2 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **.__init__()** (2 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Repository delle configurazioni tenant-aware.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Repository per le impostazioni aziendali del tenant.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Restituisce le impostazioni anagrafiche del tenant.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Crea o aggiorna le impostazioni anagrafiche del tenant.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Restituisce la configurazione SMTP del tenant.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Crea o aggiorna la configurazione SMTP del tenant.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Restituisce le numerazioni documentali del tenant.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Restituisce una singola numerazione documentale per codice.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **Crea o aggiorna una numerazione documentale del tenant.** (1 connections) — `backend/app/repositories/core/tenant_settings_repository.py`

## Relationships

- [[Tenant Encryption & Sequences]] (20 shared connections)
- [[Tenant Settings & Dashboard]] (13 shared connections)
- [[Community 58]] (3 shared connections)
- [[Settings Routes]] (2 shared connections)

## Source Files

- `backend/app/repositories/core/tenant_settings_repository.py`
- `backend/app/services/tenant_admin/tenant_settings_service.py`

## Audit Trail

- EXTRACTED: 62 (61%)
- INFERRED: 40 (39%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*