# Security Persistence and Migrations

## Obiettivo

Rendere il modulo `Auth & Identity` realmente persistito e governato da migrazioni versionate.

## Stato attuale

- `Alembic` introdotto nel backend
- migration iniziale presente
- schema PostgreSQL `security` creato automaticamente
- ruoli, permessi e utenti iniziali seedati
- refresh token persistiti
- audit log persistito
- audit amministrativo utenti persistito
- tenant applicativi persistiti
- collegamento `security.users.tenant_id` attivo
- configurazioni tenant-aware persistite nello schema `core`

## Oggetti creati nello schema `security`

- `roles`
- `permissions`
- `users`
- `tenants`
- `role_permissions`
- `refresh_tokens`
- `audit_log`

## Oggetti creati nello schema `core`

- `tenant_company_settings`
- `tenant_smtp_settings`
- `tenant_document_sequences`

## Seed iniziale

La migration iniziale crea:

- ruolo `admin`
- ruolo `user`
- permessi base per `users.read`, `users.write`, `audit.read`
- utente `admin`
- utente `user`

Le migrazioni successive aggiungono:

- ruolo `tenant_admin`
- utente `tenant.admin`
- tenant demo `Ceramica Demo S.r.l.`
- configurazione aziendale demo
- configurazione SMTP demo
- numerazioni documentali demo

## Regola operativa

Ogni modifica futura allo schema sicurezza deve passare da una nuova migration Alembic.

## Vincolo

Le migration non devono contenere logica di business generale. Devono limitarsi a evoluzione schema, seed tecnici e dati strutturali strettamente necessari.
