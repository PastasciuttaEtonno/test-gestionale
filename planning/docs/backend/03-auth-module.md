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
- refresh token persistiti in PostgreSQL con concetto di **famiglia** (`family_id`, `parent_token_identifier`, `family_created_at`)
- **reuse detection** allineata a RFC 9700 §4.13: presentare un refresh gia' ruotato revoca l'intera famiglia
- **absolute family timeout**: la famiglia di refresh non puo' vivere oltre `refresh_token_family_max_age_days` (default 14 gg)
- frontend: lock single-flight in-memory + `navigator.locks` cross-tab per serializzare i refresh paralleli (allineato a Auth0 SPA SDK)
- nessun grace period server-side: la sicurezza vince sempre, il client si occupa di non duplicare le richieste
- audit login, refresh, logout, reuse-detected, family-revoked e family-timeout persistiti su DB
- audit auth persistito con `ip_address` e `user_agent` reali
- **password breach screening** via HIBP Pwned Passwords con k-anonymity: SHA1 della password troncato a 5 caratteri, suffisso cercato localmente, password non lascia mai il backend in chiaro
- regole password aggiornate a NIST SP 800-63B: minimo 12 caratteri + blacklist valori comuni, niente complessita' forzata
- cache Redis (TTL 24h) sui prefissi HIBP per ridurre le chiamate al servizio esterno
- policy fail-open: se HIBP e' irraggiungibile la creazione utente non si blocca ma viene auditata `PASSWORD_BREACH_CHECK_FAILED`
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
- non esiste ancora una gestione completa dei tenant lato backoffice Gestionale
- il rate limiting e oggi basato su PostgreSQL e non ancora su Redis o infrastruttura distribuita
- manca ancora un motore dedicato anti-abuso distribuito basato su Redis o edge gateway
- l'endpoint self-service di cambio/reset password non esiste ancora (lo screening HIBP e' gia' integrato in `POST /users` e sara' riutilizzabile)
- MFA / TOTP non ancora implementato
- impersonation controllata per assistenza Gestionale non ancora implementata

## Refresh token family (dettaglio implementativo)

Migration: `20260527_0011_add_refresh_token_family`. Backward-compatible additive — backfill: ogni token esistente diventa una famiglia di se' stesso.

Flusso `AuthService.refresh()`:

1. decodifica JWT, estrai `jti` e `sub`
2. `RefreshTokenRepository.get_by_identifier(jti)` — SENZA filtro `revoked_at` (serve per distinguere "sconosciuto" da "riusato")
3. token assente o `user_id` mismatch → audit `REFRESH_REUSE_DETECTED` + 401
4. token con `revoked_at IS NOT NULL` → `revoke_family(family_id)` + audit `REFRESH_REUSE_DETECTED` e `REFRESH_FAMILY_REVOKED` + 401
5. `now - family_created_at > family_max_age` → `revoke_family(family_id)` + audit `REFRESH_FAMILY_TIMEOUT` + 401
6. utente non attivo → 401 senza emettere token
7. tutto ok: revoca il token corrente come `Rotazione refresh token.`, emette nuovo refresh con stessa `family_id`, `parent_token_identifier = jti corrente`, `family_created_at` preservato

Audit event types nuovi:

- `REFRESH_REUSE_DETECTED` — riuso o `jti` sconosciuto o `user_id` mismatch
- `REFRESH_FAMILY_REVOKED` — famiglia revocata in seguito a reuse
- `REFRESH_FAMILY_TIMEOUT` — famiglia chiusa per limite assoluto

Settings:

- `refresh_token_expire_days` — TTL del singolo token (default 7)
- `refresh_token_family_max_age_days` — TTL assoluto della famiglia (default 14)

## Password breach screening (dettaglio implementativo)

Servizio: `app/services/auth/password_breach_service.py`. Pattern k-anonymity:

1. calcola `sha1 = SHA1(password).upper()`
2. invia solo `prefix = sha1[:5]` a `https://api.pwnedpasswords.com/range/{prefix}` (header `Add-Padding: true` per non leakare la lunghezza esatta del payload via traffic analysis)
3. cerca `suffix = sha1[5:]` localmente nella risposta (~600-900 righe)
4. se trovato → `count` = quante volte la password e' apparsa nei breach noti

Politica: rifiuto se `count > password_breach_max_count` (default 10). Tutto al di sopra di 10 e' gia' nelle wordlist standard usate dagli attaccanti.

Audit event types nuovi:

- `PASSWORD_BREACH_REJECTED` — password rifiutata, contiene `breach_count` e `soglia`
- `PASSWORD_BREACH_CHECK_FAILED` — HIBP irraggiungibile, operazione proseguita (fail-open)

Validatore Pydantic (`CreateUserRequest.password`): blocca prima ancora di chiamare HIBP i casi banali (minimo 12 caratteri, blacklist).

Settings:

- `password_breach_check_enabled` (default `True`) — kill-switch globale
- `password_breach_max_count` (default `10`) — soglia di rifiuto
- `password_breach_api_timeout_seconds` (default `3`) — timeout HTTP
- `password_breach_cache_ttl_seconds` (default `86400`) — TTL cache Redis su prefisso

## Step successivo naturale

- introdurre MFA opzionale (TOTP) per `admin` e `tenant_admin`
- impersonation controllata super-admin → tenant con audit forte
- password breach screening (HIBP k-anonymity) su change/reset
- estendere lo scoping tenant ai primi domini business reali
- valutare una strategia piu avanzata di protezione auth con Redis quando il runtime diventa multiistanza
