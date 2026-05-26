# Tenant Admin Configuration

## Obiettivo

Descrivere il primo blocco reale di API tenant-aware dedicato alla console `Tenant Admin`.

## Perimetro attuale

Le API oggi coperte sono:

- profilo aziendale del tenant
- configurazione SMTP del tenant
- numerazioni documentali del tenant
- audit locale del tenant
- gestione utenti limitata al tenant corrente

## Schemi coinvolti

### `security`

- `tenants`
- `users.tenant_id`

### `core`

- `tenant_company_settings`
- `tenant_smtp_settings`
- `tenant_document_sequences`

## Endpoint attivi

- `GET /api/v1/tenant-admin/company-settings`
- `PUT /api/v1/tenant-admin/company-settings`
- `GET /api/v1/tenant-admin/smtp-settings`
- `PUT /api/v1/tenant-admin/smtp-settings`
- `GET /api/v1/tenant-admin/document-sequences`
- `PUT /api/v1/tenant-admin/document-sequences/{sequence_code}`
- `GET /api/v1/tenant-admin/audit-log`

## Regole di sicurezza

- accesso consentito solo al ruolo `tenant_admin`
- il `tenant_id` non arriva dal client: viene risolto dal profilo autenticato corrente
- il `tenant_admin` non puo accedere all'audit globale Gestionale
- il `tenant_admin` non puo operare su utenti di altri tenant
- la password SMTP viene accettata in chiaro solo in input API, poi cifrata lato backend
- la password SMTP non viene mai restituita nelle response

## Note di implementazione

- il service applicativo e [tenant_settings_service.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/services/tenant_admin/tenant_settings_service.py)
- la cifratura campi sensibili e centralizzata in [field_encryption.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/core/security/field_encryption.py)
- le route FastAPI sono in [settings_routes.py](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/app/api/v1/tenant_admin/settings_routes.py)

## Limiti attuali

- il logo aziendale e trattato come riferimento `logo_url`, non come upload file
- la configurazione SMTP non esegue ancora test di connettivita
- le numerazioni documentali sono aggiornabili ma non ancora collegate ai moduli fatture e bolle
- non esiste ancora una UI collegata a questi endpoint nel frontend
