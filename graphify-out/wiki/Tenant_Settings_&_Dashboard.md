# Tenant Settings & Dashboard

> 30 nodes · cohesion 0.12

## Key Concepts

- **TenantCompanySettings** (31 connections) — `backend/app/models/core/tenant_company_settings.py`
- **TenantSmtpSettings** (31 connections) — `backend/app/models/core/tenant_smtp_settings.py`
- **Tenant** (31 connections) — `backend/app/models/security/tenant.py`
- **Base** (23 connections) — `backend/app/core/db.py`
- **DashboardService** (18 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **CurrentUserResponse** (9 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **DashboardKpisResponse** (9 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **str** (9 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **.get_dashboard_kpis()** (9 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **Redis** (8 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **Session** (8 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **._load_dashboard_kpis()** (5 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **._resolve_tenant_id()** (5 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **Session** (4 connections) — `backend/app/repositories/core/tenant_settings_repository.py`
- **tenant_company_settings.py** (2 connections) — `backend/app/models/core/tenant_company_settings.py`
- **tenant_smtp_settings.py** (2 connections) — `backend/app/models/core/tenant_smtp_settings.py`
- **tenant.py** (2 connections) — `backend/app/models/security/tenant.py`
- **.__init__()** (2 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **Classe base dichiarativa per tutti i modelli ORM.** (1 connections) — `backend/app/core/db.py`
- **Modello ORM delle impostazioni aziendali del tenant.** (1 connections) — `backend/app/models/core/tenant_company_settings.py`
- **Configurazione anagrafica e documentale dell'azienda cliente.** (1 connections) — `backend/app/models/core/tenant_company_settings.py`
- **Modello ORM delle impostazioni SMTP del tenant.** (1 connections) — `backend/app/models/core/tenant_smtp_settings.py`
- **Configurazione SMTP usata dall'azienda cliente per l'invio email.** (1 connections) — `backend/app/models/core/tenant_smtp_settings.py`
- **Valida e restituisce il tenant corrente per utenti tenant-scoped.** (1 connections) — `backend/app/services/dashboard/dashboard_service.py`
- **Costruisce e memorizza in cache i KPI dashboard isolati per tenant.** (1 connections) — `backend/app/services/dashboard/dashboard_service.py`
- *... and 5 more nodes in this community*

## Relationships

- [[Tenant Encryption & Sequences]] (24 shared connections)
- [[Audit & User Models]] (22 shared connections)
- [[Tenant Settings Repository]] (13 shared connections)
- [[Bolla Repository & Events]] (8 shared connections)
- [[Articolo CRUD Methods]] (7 shared connections)
- [[Finance Cost Module]] (7 shared connections)
- [[Community 58]] (6 shared connections)
- [[Community 50]] (5 shared connections)
- [[Community 67]] (4 shared connections)
- [[Community 35]] (3 shared connections)
- [[Anagrafica Models]] (2 shared connections)
- [[Settings Routes]] (2 shared connections)

## Source Files

- `backend/app/core/db.py`
- `backend/app/models/core/tenant_company_settings.py`
- `backend/app/models/core/tenant_smtp_settings.py`
- `backend/app/models/security/tenant.py`
- `backend/app/repositories/core/tenant_settings_repository.py`
- `backend/app/services/dashboard/dashboard_service.py`

## Audit Trail

- EXTRACTED: 83 (38%)
- INFERRED: 137 (62%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*