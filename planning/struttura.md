Ecco una proposta di stesura professionale per il tuo documento di architettura. Questo file `.md` funge da **Master Plan** per la migrazione: è scritto con un approccio da Software Architect, bilanciando la scalabilità dei microservizi con la realtà operativa di un team snello.

---

# Progetto di Migrazione: Da Legacy Monolith a Modular Web Architecture

**Target Stack:** Python (FastAPI + Pydantic + SQLAlchemy) | Vue.js | Docker | PostgreSQL

## 1. Visione dell'Architettura

L'obiettivo è trasformare il gestionale desktop (VB6/VB.NET) in una Web App moderna. Sebbene il termine "microservizi" sia il target finale, per un team di dimensioni ridotte adotteremo un approccio **Modular Monolith containerizzato**. Questo permette di separare logicamente i domini (Fatture, Spedizioni, Anagrafiche) senza l'eccessiva complessità di gestione di decine di database separati.

---

## 2. Lo Stack Tecnologico (The Tech Stack)

| Layer | Tecnologia | Motivazione |
| --- | --- | --- |
| **Frontend** | **Vue.js 3 (Vite)** | Più intuitivo di React, curva di apprendimento rapida, eccellente per interfacce gestionali pesanti. |
| **Backend** | **Python (FastAPI + Pydantic + SQLAlchemy)** | FastAPI per API e OpenAPI, Pydantic per validazione/serializzazione dei contratti, SQLAlchemy come layer ORM e mapping verso PostgreSQL. |
| **Database** | **PostgreSQL** | Supporto avanzato per **Materialized Views**, JSONB per dati semistrutturati e robustezza ACID. |
| **Container** | **Docker & Compose** | Isolamento totale dell'ambiente di sviluppo e produzione. |
| **Cache/Broker** | **Redis** | Per la gestione delle sessioni e code di messaggi (es. invio massivo fatture). |

---

## 3. Schema dell'Infrastruttura (Dockerization)

Ogni componente dell'app vivrà in un container dedicato per garantire portabilità e conformità **NIS2**.

### Servizi Definiti (docker-compose):

1. **`client`**: Il frontend Vue.js servito tramite Nginx.
2. **`api_gateway`**: Punto di ingresso unico (Nginx o Traefik) che gestisce SSL e routing.
3. **`core_service`**: Il backend Python FastAPI che gestisce la logica di business.
4. **`worker_service`**: Un'istanza Python dedicata a task pesanti (generazione PDF, invio XML SdI).
5. **`db_service`**: PostgreSQL per la persistenza dei dati.

---

## 4. Specifiche del Backend (Python/FastAPI)

Il backend deve essere progettato seguendo i principi della **Clean Architecture**.

* **Struttura delle Cartelle:**
* `app/api/`: Endpoint REST (v1, v2).
* `app/core/`: Configurazioni globali e sicurezza (JWT, NIS2 compliance).
* `app/models/`: Definizione degli schemi database tramite SQLAlchemy ORM.
* `app/services/`: Logica di business (qui viene "tradotta" la logica del vecchio VB).
* `app/schemas/`: Modelli Pydantic per validazione, serializzazione e contratti API.

### Modulo Trasversale di Sicurezza

Come primo asse di implementazione si introduce un modulo trasversale `Auth & Identity`, interno al `core_service`, responsabile di autenticazione multiutente, ruoli, audit e collegamento futuro tra utente applicativo e profilo anagrafico. La specifica tecnica di dettaglio e contenuta in [auth-module-spec.md](c:/Users/ivan.lisciotto_webra/Desktop/project/planning/auth-module-spec.md).



---

## 5. Specifiche del Frontend (Vue.js)

Abbiamo scelto Vue.js per la sua semplicità nella gestione dei form complessi (tipici di bolle e fatture).

* **State Management:** **Pinia** (standard moderno per Vue 3).
* **UI Component Library:** **Tailwind CSS + PrimeVue** (componenti pronti per tabelle dati, filtri e calendari).
* **Comunicazione:** Axios con interceptor per la gestione automatica dei token JWT.

---

## 6. Regole di Buona Stesura (Coding Standards)

Per garantire che il codice sia manutenibile per i prossimi 10 anni:

### Backend

* **PEP 8 Compliance:** Obbligatorio l'uso di `black` o `ruff` per la formattazione.
* **Type Hinting:** Ogni funzione Python deve avere i tipi definiti (es. `def calcola_iva(prezzo: float) -> float:`).
* **Docstrings:** Formato Google Style per ogni classe e metodo complesso.

### Database

* **Naming Convention:** Snake_case per tabelle e colonne.
* **Migrations:** Uso tassativo di **Alembic**. Nessuna modifica manuale allo schema del DB.

---

## 7. Documentazione e Compliance

### Documentazione Tecnica

* **API:** Accessibile via `/docs` (Swagger UI) generata automaticamente da FastAPI.
* **Architettura:** Wiki interna (es. Obsidian o Notion) che spieghi il mapping tra i vecchi file VB e i nuovi moduli Python.

### Sicurezza (NIS2 Ready)

* **Logging:** Ogni operazione di scrittura deve essere loggata (Audit Log).
* **Secrets:** Nessuna password nel codice. Uso esclusivo di variabili d'ambiente (`.env`) gestite tramite Docker Secrets.

---

## 8. Piano di Migrazione (The "Strangler" Strategy)

1. **Analisi DB:** Mappare le tabelle del vecchio SQL Server/Access al nuovo PostgreSQL.
2. **Modulo Anagrafiche:** Primo container ad andare in produzione (il più semplice).
3. **Modulo Documentale:** Sviluppo di Bolle e Spedizioni (integrazione API corrieri).
4. **Modulo Fiscale:** Fatturazione elettronica e chiusura del cerchio.

---

> **Nota dell'Architetto:** "L'eleganza di un software non sta in quanto è complesso, ma in quanto è facile da cambiare quando le leggi fiscali cambiano."

---

