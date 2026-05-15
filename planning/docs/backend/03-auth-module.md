# Auth Module

## Obiettivo

Costruire il primo modulo trasversale di piattaforma:

- autenticazione
- autorizzazione
- audit
- collegamento futuro a profilo anagrafico

## Confini

Il modulo `Auth`:

- protegge i moduli futuri
- non dipende da `Anagrafiche`
- non contiene logica fiscale o documentale

## Stato corrente

- endpoint `login`, `refresh`, `logout`, `me` attivi
- utenti iniziali `admin`, `tenant.admin` e `user` seedati via migration
- JWT reali emessi dal backend
- refresh token persistiti in PostgreSQL
- audit login e refresh persistito su DB
- audit esteso a creazione utente, aggiornamento utente, cambio stato e cambio ruolo
- `users` e `audit-log` letti dal database reale
- ruolo reale `tenant_admin` introdotto nel dominio sicurezza
- dependency disponibili per `tenant_admin` e per il caso `admin` o `tenant_admin`
- introdotto schema logico `tenant` con collegamento `user.tenant_id`
- `tenant_admin` autenticato con `tenant_id` nel profilo corrente
- gestione utenti resa tenant-aware
- audit locale tenant disponibile tramite endpoint dedicato

## Limiti attuali

- lo scoping tenant e oggi applicato a utenti e audit locale, non ancora ai futuri domini business come anagrafiche, bolle o fatture
- non esiste ancora una gestione completa dei tenant lato backoffice Esseduesoft
- manca ancora il tracciamento di `ip_address` e `user_agent` reali negli eventi audit

## Step successivo naturale

- introdurre test automatici API
- preparare il collegamento tra `user` e futuro profilo anagrafico
- estendere lo scoping tenant ai primi domini business reali
- valutare acquisizione di `ip_address` e `user_agent` reali negli eventi audit
