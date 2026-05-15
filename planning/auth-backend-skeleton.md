# Skeleton Architetturale Backend: Modulo Auth

## 1. Obiettivo

Definire la struttura concreta del backend FastAPI necessaria a ospitare il modulo `Auth & Identity`, senza introdurre ancora business logic applicativa.

Questo skeleton serve a:

- fissare la struttura del progetto backend
- esplicitare responsabilita per package
- chiarire i punti di estensione futuri
- ridurre il rischio di accoppiamento tra sicurezza e domini funzionali

---

## 2. Principio Guida

Il modulo `Auth` va implementato come modulo interno del `core_service`, ma con isolamento logico sufficiente da poter evolvere autonomamente.

Quindi:

- separazione chiara tra API, servizi, persistenza e policy
- dipendenze unidirezionali dall'esterno verso il dominio di sicurezza
- nessuna dipendenza diretta del modulo `Auth` da `Anagrafiche`
- predisposizione di interfacce e placeholder per il futuro `person_id`

---

## 3. Struttura Directory Consigliata

```text
backend/
  app/
    api/
      deps/
        auth.py
      v1/
        router.py
        auth/
          routes.py
        users/
          routes.py
        admin/
          routes.py
    core/
      config.py
      db.py
      logging.py
      security/
        hashing.py
        jwt.py
        permissions.py
        policies.py
    models/
      base.py
      security/
        user.py
        role.py
        permission.py
        role_permission.py
        refresh_token.py
        audit_log.py
    repositories/
      security/
        user_repository.py
        role_repository.py
        refresh_token_repository.py
        audit_repository.py
    schemas/
      auth/
        requests.py
        responses.py
      users/
        requests.py
        responses.py
      audit/
        responses.py
    services/
      auth/
        auth_service.py
        token_service.py
        session_service.py
      users/
        user_service.py
      audit/
        audit_service.py
    domain/
      security/
        enums.py
        constants.py
        exceptions.py
    main.py
```

---

## 4. Responsabilita per Livello

### 4.1 `api/`

Responsabilita:

- esposizione endpoint REST
- parsing richieste
- validazione input via schema
- delega ai servizi applicativi
- applicazione dependency di autenticazione/autorizzazione

Non deve contenere:

- query SQL
- logica di token handling complessa
- decisioni di business

### 4.2 `core/security/`

Responsabilita:

- hashing password
- creazione e validazione JWT
- policy di autorizzazione
- helper di sicurezza riusabili

Questa cartella ospita la meccanica tecnica della sicurezza.

### 4.3 `models/security/`

Responsabilita:

- definizione ORM delle entita persistenti del modulo sicurezza

Include:

- `User`
- `Role`
- `Permission`
- `RolePermission`
- `RefreshToken`
- `AuditLog`

### 4.4 `repositories/security/`

Responsabilita:

- accesso ai dati
- caricamento e persistenza entita
- isolamento del livello SQLAlchemy/SQLModel dal resto del codice

### 4.5 `services/`

Responsabilita:

- orchestrazione dei casi d'uso
- coordinamento tra repository, security helpers e audit

Qui risiede la vera logica applicativa del modulo `Auth`.

### 4.6 `domain/security/`

Responsabilita:

- eccezioni di dominio
- enum e costanti
- definizioni concettuali riusabili

Esempi:

- `RoleCode`
- `AuditEventType`
- `PermissionCode`
- `InvalidCredentialsError`
- `InactiveUserError`

---

## 5. Entry Point e Wiring

### 5.1 `main.py`

Responsabilita:

- bootstrap FastAPI
- registrazione router principali
- configurazione middleware
- inizializzazione logging

### 5.2 `api/v1/router.py`

Responsabilita:

- composizione del router v1

Router minimi:

- `auth`
- `users`
- `admin`

### 5.3 `api/deps/auth.py`

Responsabilita:

- ottenere utente corrente
- validare account attivo
- verificare ruolo `admin`
- verificare permesso specifico

Questo file diventa il punto standard con cui tutti i moduli futuri proteggeranno gli endpoint.

---

## 6. Entita Minime da Modellare

### 6.1 `User`

Campi attesi:

- `id`
- `username`
- `email` opzionale se non ancora deciso come login principale
- `password_hash`
- `role_code`
- `is_active`
- `person_id`
- `legacy_reference`
- `last_login_at`
- `created_at`
- `updated_at`

### 6.2 `Role`

Campi attesi:

- `code`
- `name`
- `description`

### 6.3 `Permission`

Campi attesi:

- `code`
- `name`
- `description`

### 6.4 `RolePermission`

Campi attesi:

- `role_code`
- `permission_code`

### 6.5 `RefreshToken`

Campi attesi:

- `id`
- `user_id`
- `token_identifier`
- `issued_at`
- `expires_at`
- `revoked_at`
- `revoked_reason`
- `ip_address`
- `user_agent`

### 6.6 `AuditLog`

Campi attesi:

- `id`
- `user_id`
- `event_type`
- `resource_type`
- `resource_id`
- `payload_json`
- `ip_address`
- `user_agent`
- `created_at`

---

## 7. Schemi API Minimi

### 7.1 `schemas/auth/requests.py`

Contenuti attesi:

- `LoginRequest`

### 7.2 `schemas/auth/responses.py`

Contenuti attesi:

- `AuthSessionResponse`
- `CurrentUserResponse`
- `LogoutResponse`

### 7.3 `schemas/users/requests.py`

Contenuti attesi:

- `CreateUserRequest`
- `UpdateUserRequest`
- `ChangeUserStatusRequest`
- `ChangeUserRoleRequest`

### 7.4 `schemas/users/responses.py`

Contenuti attesi:

- `UserResponse`
- `UserListResponse`

### 7.5 `schemas/audit/responses.py`

Contenuti attesi:

- `AuditLogResponse`
- `AuditLogListResponse`

---

## 8. Servizi Applicativi Minimi

### 8.1 `AuthService`

Responsabilita:

- validare credenziali
- coordinare login
- coordinare logout
- recuperare utente corrente

### 8.2 `TokenService`

Responsabilita:

- generare access token
- generare refresh token
- validare token
- gestire rotazione refresh token

### 8.3 `SessionService`

Responsabilita:

- persistere sessioni o refresh token
- revocare sessioni
- gestire invalidazioni

### 8.4 `UserService`

Responsabilita:

- creare utenti
- aggiornare utenti
- attivare/disattivare account
- assegnare ruoli

### 8.5 `AuditService`

Responsabilita:

- registrare eventi
- serializzare payload minimi
- esporre consultazione audit

---

## 9. Router Minimi

### 9.1 `auth/routes.py`

Endpoint attesi:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Note operative:

- `login` imposta il refresh token come cookie `HttpOnly`
- `refresh` legge il refresh token dal cookie e non dal body
- `logout` revoca la sessione e rimuove il cookie

### 9.2 `users/routes.py`

Endpoint attesi:

- `GET /api/v1/users`
- `GET /api/v1/users/{id}`
- `POST /api/v1/users`
- `PATCH /api/v1/users/{id}`
- `PATCH /api/v1/users/{id}/status`
- `PATCH /api/v1/users/{id}/role`

### 9.3 `admin/routes.py`

Endpoint attesi:

- `GET /api/v1/admin/audit-log`

---

## 10. Policy di Dipendenza tra Moduli

Per evitare degrado architetturale, i moduli futuri devono usare `Auth` in questo modo:

- possono dipendere da dependency di autenticazione/autorizzazione
- possono leggere `current_user`
- possono usare `person_id` come collegamento verso il profilo canonico
- non devono conoscere il funzionamento interno di token, sessioni o audit

Inversamente, `Auth` non deve importare o dipendere dai moduli `Anagrafiche`, `Documentale` o `Fiscale`.

---

## 11. Requisiti Minimi di Configurazione

Da gestire in `core/config.py`:

- secret key JWT
- algoritmo JWT
- durata access token
- durata refresh token
- nome e policy del cookie refresh
- origini CORS consentite con `allow_credentials`
- issuer e audience se adottati
- policy password minima
- rate limiting login se previsto via middleware o gateway

---

## 12. Logging e Audit

Separare chiaramente:

- `application logs`
- `security audit logs`

Il logging applicativo serve a diagnosi tecnica.
L'audit serve a tracciabilita operativa e sicurezza.

Questo evita che eventi sensibili si perdano nei log generici.

---

## 13. Vincoli per la Fase di Implementazione

- nessuna business logic di dominio nel modulo `Auth`
- nessuna FK forte verso anagrafiche finche il modello non e stabilizzato
- nessun controllo ruoli hardcoded sparso nei router
- nessun accesso DB diretto dentro gli endpoint
- nessuna dipendenza dal frontend

---

## 14. Sequenza di Avvio Consigliata

1. bootstrap progetto FastAPI
2. introduzione struttura cartelle
3. configurazione DB e base model
4. definizione entita `security`
5. definizione schemi Pydantic
6. wiring router v1
7. introduzione servizi `AuthService`, `TokenService`, `AuditService`
8. dependency `current_user` e `require_admin`
9. predisposizione CRUD utenti

---

## 15. Esito Atteso

A valle di questo skeleton il team deve avere:

- un backend con struttura coerente e scalabile
- un modulo `Auth` isolato e riusabile
- punti di estensione chiari per domini futuri
- una base sicura per implementare `Anagrafiche`

Questo e il livello corretto di preparazione prima di scrivere la logica concreta di autenticazione e gestione utenti.
