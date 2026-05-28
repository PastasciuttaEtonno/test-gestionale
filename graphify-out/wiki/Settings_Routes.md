# Settings Routes

> 30 nodes · cohesion 0.13

## Key Concepts

- **TenantSettingsService** (32 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **settings_routes.py** (9 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **update_document_sequence()** (8 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **TenantSettingsService** (8 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **CurrentUserResponse** (7 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **update_company_settings()** (7 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **update_smtp_settings()** (7 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **get_company_settings()** (5 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **get_smtp_settings()** (5 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **list_document_sequences()** (5 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **Redis** (4 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **get_tenant_settings_service()** (4 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **CompanySettingsResponse** (3 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **SmtpSettingsResponse** (3 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **DocumentSequenceListResponse** (2 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **DocumentSequenceResponse** (2 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **Session** (2 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **str** (2 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **UpdateCompanySettingsRequest** (2 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **UpdateDocumentSequenceRequest** (2 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **UpdateSmtpSettingsRequest** (2 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **Route di configurazione tenant admin.** (1 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **Restituisce la configurazione SMTP della propria azienda senza esporre la passwo** (1 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **Aggiorna la configurazione SMTP del tenant cifrando la password lato backend.** (1 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- **Restituisce le numerazioni configurate per la propria organizzazione.** (1 connections) — `backend/app/api/v1/tenant_admin/settings_routes.py`
- *... and 5 more nodes in this community*

## Relationships

- [[Tenant Encryption & Sequences]] (11 shared connections)
- [[Community 58]] (3 shared connections)
- [[Community 42]] (2 shared connections)
- [[Tenant Settings Repository]] (2 shared connections)
- [[Tenant Settings & Dashboard]] (2 shared connections)

## Source Files

- `backend/app/api/v1/tenant_admin/settings_routes.py`
- `backend/app/services/tenant_admin/tenant_settings_service.py`

## Audit Trail

- EXTRACTED: 100 (77%)
- INFERRED: 30 (23%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*