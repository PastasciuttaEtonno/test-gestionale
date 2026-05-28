# Tenant Encryption & Sequences

> 40 nodes · cohesion 0.10

## Key Concepts

- **TenantRepository** (40 connections) — `backend/app/repositories/security/tenant_repository.py`
- **TenantDocumentSequence** (31 connections) — `backend/app/models/core/tenant_document_sequence.py`
- **FieldEncryptionService** (21 connections) — `backend/app/core/security/field_encryption.py`
- **CurrentUserResponse** (13 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **.update_smtp_settings()** (11 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **Redis** (10 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **.update_document_sequence()** (10 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **SmtpSettingsResponse** (9 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **._get_current_tenant()** (9 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **._invalidate_dashboard_kpis_cache()** (9 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **DocumentSequenceResponse** (8 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **str** (8 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **TenantSmtpSettings** (8 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **DocumentSequenceListResponse** (7 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **TenantDocumentSequence** (7 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **UpdateDocumentSequenceRequest** (7 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **UpdateSmtpSettingsRequest** (7 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **.get_smtp_settings()** (7 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **.list_document_sequences()** (6 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **._to_sequence_response()** (6 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **._to_smtp_response()** (6 connections) — `backend/app/services/tenant_admin/tenant_settings_service.py`
- **field_encryption.py** (2 connections) — `backend/app/core/security/field_encryption.py`
- **tenant_document_sequence.py** (2 connections) — `backend/app/models/core/tenant_document_sequence.py`
- **Session** (2 connections) — `backend/app/repositories/security/tenant_repository.py`
- **.__init__()** (2 connections) — `backend/app/repositories/security/tenant_repository.py`
- *... and 15 more nodes in this community*

## Relationships

- [[Tenant Settings & Dashboard]] (24 shared connections)
- [[Tenant Settings Repository]] (20 shared connections)
- [[Community 58]] (15 shared connections)
- [[Settings Routes]] (11 shared connections)
- [[Report Task Routes]] (5 shared connections)
- [[User Management]] (5 shared connections)
- [[Audit & User Models]] (5 shared connections)
- [[Community 34]] (4 shared connections)
- [[Community 48]] (3 shared connections)
- [[Bolla Repository & Events]] (2 shared connections)
- [[Community 77]] (2 shared connections)
- [[Community 39]] (2 shared connections)

## Source Files

- `backend/app/core/security/field_encryption.py`
- `backend/app/models/core/tenant_document_sequence.py`
- `backend/app/repositories/security/tenant_repository.py`
- `backend/app/services/tenant_admin/tenant_settings_service.py`

## Audit Trail

- EXTRACTED: 120 (46%)
- INFERRED: 143 (54%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*