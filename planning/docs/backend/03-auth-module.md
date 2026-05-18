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
- audit login, refresh e logout persistito su DB
- audit auth persistito con `ip_address` e `user_agent` reali
- audit esteso a creazione utente, aggiornamento utente, cambio stato e cambio ruolo
- `users` e `audit-log` letti dal database reale
- ruolo reale `tenant_admin` introdotto nel dominio sicurezza
- dependency disponibili per `tenant_admin` e per il caso `admin` o `tenant_admin`
- introdotto schema logico `tenant` con collegamento `user.tenant_id`
- `tenant_admin` autenticato con `tenant_id` nel profilo corrente
- catalogo RBAC esteso con ruoli `manager` e `worker`
- permessi demo tenant-aware introdotti: `bom.read`, `finance.costs.write`, `bom.delete`
- autorizzazione dichiarativa lato FastAPI tramite `RequirePermission`
- gestione utenti resa tenant-aware
- audit locale tenant disponibile tramite endpoint dedicato
- protezione login persistita attiva su tre scope: `identifier + ip_address`, solo `identifier`, solo `ip_address`
- cooldown attivo con risposta `429` quando una delle soglie viene superata
- endpoint `login` e `refresh` protetti anche da controllo `Origin` / `Referer` configurabile
- configurazione runtime con fail-fast in staging e produzione su secret JWT placeholder, cookie insicuri e origin check disattivato
- `X-Forwarded-For` considerato solo se la richiesta arriva da proxy esplicitamente fidato

## Limiti attuali

- lo scoping tenant e oggi applicato a utenti e audit locale, non ancora ai futuri domini business come anagrafiche, bolle o fatture
- non esiste ancora una gestione completa dei tenant lato backoffice Esseduesoft
- il rate limiting e oggi basato su PostgreSQL e non ancora su Redis o infrastruttura distribuita
- manca ancora una session policy completa con assolute timeout lato sessione refresh e reuse detection per famiglie di refresh token
- manca ancora un motore dedicato anti-abuso distribuito basato su Redis o edge gateway
- manca ancora una policy password moderna completa per cambio/reset password con controllo password compromesse

## Step successivo naturale

- introdurre test automatici API
- preparare il collegamento tra `user` e futuro profilo anagrafico
- estendere lo scoping tenant ai primi domini business reali
- introdurre reuse detection e revoca di famiglia per refresh token
- valutare una strategia piu avanzata di protezione auth con Redis quando il runtime diventa multiistanza
