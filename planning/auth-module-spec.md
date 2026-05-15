# Specifica Tecnica: Modulo Auth & Identity

## 1. Obiettivo

Definire il modulo trasversale di autenticazione e autorizzazione per la nuova piattaforma web Esseduesoft, basata su FastAPI, Vue.js e PostgreSQL.

Questo modulo nasce come componente di piattaforma del `core_service` e ha i seguenti obiettivi:

- autenticare gli utenti applicativi
- autorizzare l'accesso alle funzionalita in base a ruoli e permessi
- tracciare gli eventi di sicurezza e le operazioni sensibili
- predisporre il collegamento tra utente applicativo e futuro profilo anagrafico
- fornire una base riutilizzabile per tutti i moduli successivi

Il modulo non va implementato come microservizio separato in questa fase. Va mantenuto come modulo interno del modular monolith.

---

## 2. Principi Architetturali

### 2.1 Posizionamento

Il modulo `Auth` deve essere trattato come servizio trasversale di piattaforma, con ownership tecnica indipendente dai domini funzionali come `Anagrafiche`, `Documentale` e `Fiscale`.

### 2.2 Responsabilita

Il modulo e responsabile di:

- gestione identita applicative
- verifica credenziali
- emissione e rinnovo token
- revoca sessioni
- gestione ruoli
- predisposizione permessi granulari
- audit degli eventi di sicurezza
- collegamento futuro tra utente e profilo anagrafico

Il modulo non e responsabile di:

- logica di business di anagrafiche, ordini, bolle o fatture
- gestione diretta del profilo cliente/fornitore/agente
- reporting analitico

### 2.3 Vincoli

- autenticazione multiutente obbligatoria fin dalla prima release
- ruoli iniziali reali attualmente implementati: `admin`, `tenant_admin`, `user`
- audit obbligatorio per accessi ed eventi sensibili
- compatibilita con futura evoluzione da ruoli semplici a permessi granulari
- integrazione con futuro dominio anagrafico senza accoppiamento prematuro
- tenant scoping lato backend obbligatorio per i moduli di livello 2

---

## 3. Struttura Logica del Modulo

Il modulo puo essere suddiviso logicamente nei seguenti sottoblocchi:

- `auth`
  - login
  - refresh token
  - logout
  - session lifecycle
- `users`
  - gestione utenti applicativi
  - stato account
  - attivazione/disattivazione
- `roles_permissions`
  - ruoli base
  - mapping permessi
  - evoluzione futura verso autorizzazioni piu fini
- `audit`
  - registrazione eventi di sicurezza
  - tracciamento operazioni sensibili
- `identity_links`
  - collegamento tra utente applicativo e profilo anagrafico futuro

---

## 4. Collocazione nel Progetto FastAPI

Struttura consigliata:

```text
app/
  api/
    v1/
      auth/
      users/
      admin/
  core/
    config/
    security/
  models/
    security/
  schemas/
    auth/
    users/
    audit/
  services/
    auth/
    users/
    audit/
  repositories/
    security/
```

Note:

- `app/core/security/` contiene policy, token handling, hashing, dependency di accesso
- `app/models/security/` contiene il modello dati persistente
- `app/services/auth/` contiene i casi d'uso applicativi
- `app/repositories/security/` isola l'accesso al database

---

## 5. Strategia di Autenticazione

### 5.1 Scelta

Per il contesto attuale, la scelta piu pragmatica e:

- `JWT access token` a vita breve
- `refresh token` persistito e revocabile

### 5.2 Motivazioni

- si integra bene con frontend Vue.js
- evita sessioni server-side classiche come modello principale
- semplifica la protezione delle API
- consente controllo sulle sessioni tramite refresh token persistiti

### 5.3 Linee guida operative

- access token breve durata
- refresh token memorizzato in persistenza con revoca esplicita
- password hash con algoritmo robusto come `Argon2` o `bcrypt`
- rotazione refresh token raccomandata
- invalidazione token in caso di disattivazione utente o reset credenziali

---

## 6. Modello Dati Iniziale

Si raccomanda uno schema PostgreSQL dedicato, ad esempio `security`.

### 6.1 Tabella `security.users`

Scopo: identita applicativa principale.

Campi minimi:

- `id`
- `username` oppure `email`
- `password_hash`
- `is_active`
- `is_superuser` opzionale se si vuole distinguere da `admin`
- `role_code`
- `person_id` nullable
- `legacy_reference` nullable
- `last_login_at`
- `created_at`
- `updated_at`

Note:

- `person_id` e una FK futura verso il profilo anagrafico canonico
- `legacy_reference` serve per tracciare l'eventuale identita legacy
- `person_id` puo restare nullo nella prima fase

### 6.2 Tabella `security.roles`

Scopo: definizione dei ruoli applicativi.

Campi minimi:

- `code`
- `name`
- `description`

Valori iniziali / attuali:

- `admin`
- `tenant_admin`
- `user`

### 6.3 Tabella `security.permissions`

Scopo: predisporre il modello per autorizzazioni granulari future.

Campi minimi:

- `code`
- `name`
- `description`

Esempi:

- `users.read`
- `users.write`
- `anagraphics.read`
- `anagraphics.write`
- `audit.read`
- `documents.export`

### 6.4 Tabella `security.role_permissions`

Scopo: mapping molti-a-molti tra ruoli e permessi.

Campi minimi:

- `role_code`
- `permission_code`

### 6.5 Tabella `security.refresh_tokens`

Scopo: gestione sessioni e revoca token.

Campi minimi:

- `id`
- `user_id`
- `token_identifier`
- `issued_at`
- `expires_at`
- `revoked_at`
- `revoked_reason`
- `ip_address`
- `user_agent`

### 6.6 Tabella `security.audit_log`

Scopo: tracciamento eventi di sicurezza e operazioni sensibili.

Campi minimi:

- `id`
- `user_id` nullable in caso di login fallito
- `event_type`
- `resource_type`
- `resource_id`
- `payload_json`
- `ip_address`
- `user_agent`
- `created_at`

---

## 7. Collegamento al Futuro Dominio Anagrafico

L'utente applicativo non va accoppiato direttamente a un tipo specifico di anagrafica.

Scelta corretta:

- `user` = identita applicativa
- `person/profile` = identita anagrafica canonica futura
- `user.person_id` = collegamento tra identita applicativa e profilo anagrafico

Motivazione:

un utente potrebbe rappresentare in futuro:

- personale interno
- agente
- referente cliente
- referente fornitore

Quindi il modulo `Auth` deve dipendere da un'astrazione di profilo, non da una specifica entita commerciale.

---

## 8. API Minime del Modulo

### 8.1 Endpoint pubblici

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

### 8.2 Endpoint autenticati

- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

### 8.3 Endpoint amministrativi

- `GET /api/v1/users`
- `GET /api/v1/users/{id}`
- `POST /api/v1/users`
- `PATCH /api/v1/users/{id}`
- `PATCH /api/v1/users/{id}/status`
- `PATCH /api/v1/users/{id}/role`
- `GET /api/v1/admin/audit-log`
- `GET /api/v1/tenant-admin/audit-log`
- `GET /api/v1/tenant-admin/company-settings`
- `PUT /api/v1/tenant-admin/company-settings`
- `GET /api/v1/tenant-admin/smtp-settings`
- `PUT /api/v1/tenant-admin/smtp-settings`
- `GET /api/v1/tenant-admin/document-sequences`
- `PUT /api/v1/tenant-admin/document-sequences/{sequence_code}`

### 8.4 Contratti minimi attesi

`login`

- input: credenziale + password
- output: access token + refresh token + profilo base utente

`refresh`

- input: refresh token valido
- output: nuovo access token e refresh token aggiornato se prevista rotazione

`logout`

- input: contesto utente autenticato
- effetto: revoca refresh token o sessione corrente

`me`

- output: identita corrente, ruolo, permessi assegnati, stato account, eventuale `person_id`

---

## 9. Regole di Autorizzazione

### 9.1 Ruoli iniziali / attuali

`admin`

- gestione utenti
- assegnazione ruoli
- consultazione audit
- accesso completo ai moduli abilitati
- visione globale Esseduesoft

`tenant_admin`

- gestione utenti del proprio tenant
- consultazione audit locale del proprio tenant
- configurazione aziendale del proprio tenant
- configurazione SMTP del proprio tenant
- configurazione numerazioni documentali del proprio tenant
- nessun accesso al perimetro globale Esseduesoft

`user`

- accesso alle sole funzionalita autorizzate
- nessuna gestione amministrativa utenti

### 9.2 Linea guida

Anche se oggi i ruoli sono pochi, le verifiche lato backend devono essere implementate su permessi o policy, non su semplici `if role == admin` diffusi nel codice.

Questo evita di dover rifattorizzare il modulo quando emergeranno ruoli come:

- amministrazione
- logistica
- commerciale
- responsabile magazzino
- responsabile IT tenant

### 9.3 Dependency applicative da predisporre

- utente autenticato corrente
- utente attivo
- controllo ruolo `admin`
- controllo ruolo `tenant_admin`
- controllo permesso specifico

---

## 10. Audit e Tracciabilita

Eventi minimi da registrare:

- login riuscito
- login fallito
- refresh token
- logout
- creazione utente
- modifica utente
- disattivazione utente
- riattivazione utente
- cambio ruolo
- tentativo di accesso negato

Linee guida:

- non loggare password o segreti
- limitare `payload_json` a metadati utili
- registrare sempre timestamp, utente, IP e user-agent se disponibili
- rendere consultabile l'audit agli utenti autorizzati

---

## 11. Flussi Minimi

### 11.1 Login

1. L'utente invia credenziali
2. Il sistema valida l'account
3. Il sistema verifica la password
4. Il sistema genera access token
5. Il sistema persiste refresh token
6. Il sistema registra audit di login
7. Il sistema restituisce il profilo utente base

### 11.2 Logout

1. L'utente richiede logout
2. Il sistema revoca la sessione corrente o il refresh token associato
3. Il sistema registra audit di logout

### 11.3 Accesso a endpoint protetto

1. Il token viene validato
2. Il sistema verifica stato utente
3. Il sistema verifica ruolo o permesso richiesto
4. In caso di diniego, registra evento di accesso negato

---

## 12. Integrazione con Frontend Vue.js

Linee guida minime:

- storage coerente dei token secondo policy di sicurezza scelta
- interceptor Axios per allegare access token
- gestione automatica del refresh in caso di scadenza access token
- logout applicativo in caso di refresh non valido
- inizializzazione store utente tramite endpoint `me`

Il frontend non deve contenere la logica di autorizzazione come unica fonte di verita. I controlli reali restano lato backend.

---

## 13. Vincoli di Sicurezza

- nessuna password in chiaro
- segreti applicativi via variabili d'ambiente o secret manager
- rate limiting raccomandato sugli endpoint di login
- account disabilitabile senza cancellazione fisica
- revoca sessioni disponibile lato backend
- audit non disattivabile dai client

---

## 14. Ordine di Implementazione Consigliato

1. schema `security`
2. modello `users`, `roles`, `permissions`, `role_permissions`
3. modello `refresh_tokens` e `audit_log`
4. servizio `login / refresh / logout / me`
5. dependency di autorizzazione
6. CRUD amministrativo utenti
7. consultazione audit
8. introduzione `tenants` e `user.tenant_id`
9. API tenant-aware per utenti, audit locale e configurazione aziendale
10. predisposizione collegamento `person_id`

---

## 15. Decisioni Gia Fissate

- il modulo `Auth` nasce interno al modular monolith
- `admin`, `tenant_admin` e `user` sono i ruoli iniziali reali
- il sistema deve supportare audit fin dalla prima release
- il collegamento all'anagrafica futura deve essere previsto ma non accoppiato rigidamente
- il modello autorizzativo deve essere predisposto per crescita futura
- i primi endpoint tenant-aware sono gia stati introdotti per il livello 2

---

## 16. Decisioni Ancora Aperte

Da chiarire prima dell'implementazione completa:

- identificativo primario di login: `username`, `email` o entrambi
- policy password
- durata access token e refresh token
- strategia frontend per memorizzazione token
- perimetro iniziale di consultazione audit
- eventuale necessità futura di MFA
- definizione del dominio anagrafico che alimentera `person_id`

---

## 17. Esito Architetturale

Questa impostazione consente di:

- iniziare la piattaforma da un asse trasversale stabile
- proteggere i moduli futuri con criteri coerenti
- evitare accoppiamenti prematuri con il dominio anagrafiche
- introdurre da subito audit e controllo accessi
- mantenere compatibilita con una crescita futura verso ruoli e permessi piu articolati
