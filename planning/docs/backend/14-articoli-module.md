# Modulo Articoli

## Obiettivo

Secondo modulo business tenant-aware del gestionale. Gestisce il catalogo di prodotti e
materiali dell'azienda cliente (per il dominio ceramica/logistica: piastrelle, sanitari,
accessori, materiali di posa). E' il nodo che i futuri documenti — bolle/DDT e fatture —
referenzieranno per le righe documento.

E' costruito sullo stesso pattern a layer di Anagrafiche (model → repository → service →
routes) e riusa identico il meccanismo di tenant scoping gia' validato.

## Perimetro della v1

### In scope

- Catalogo articoli tenant-aware con CRUD completo
- Categorie articolo come tabella lookup tenant-aware (CRUD)
- Campi commerciali/fiscali: codice interno, prezzo unitario, aliquota IVA, unita' di misura
- Giacenza come campo semplice sull'articolo (quantita' corrente, aggiornata manualmente)
- Optimistic locking via campo `version` (primo modulo a introdurlo)
- Eventi SSE su create/update/deactivate + KPI dashboard live "Articoli a catalogo"
- Filtri lista: categoria, attivo/disattivo, ricerca testuale (codice/descrizione)

### Out of scope v1 (moduli futuri)

- Movimenti di magazzino (carico/scarico) con storico e giacenza calcolata
- Listini multipli / prezzi per cliente o quantita'
- Varianti articolo (taglie, colori, lotti)
- Distinta base (BOM) reale
- Import da CSV / legacy
- Immagini/allegati articolo

---

## Decisioni di design

### 1. Soldi in Decimal, mai Float

`prezzo_unitario` e `aliquota_iva` sono `NUMERIC` (Decimal), non `FLOAT`. Coerente con
`production-readiness-gap-analysis.md §5`: gli importi vanno in decimal per evitare errori di
arrotondamento, inaccettabili quando l'articolo finira' nelle righe di una fattura.

### 2. Optimistic locking (`version`)

Articoli e' il primo modulo a introdurre il campo `version` raccomandato dal
`gap-analysis §6` (concurrency). Su `PATCH`, il payload deve includere `version`; il service
confronta:

- match → applica modifica, `version += 1`
- mismatch → `409 Conflict` "Articolo modificato da un altro utente, ricarica la pagina"

Il pattern sara' ereditato dai prossimi moduli business (bolle, fatture).

### 3. Categoria come lookup tenant-aware

`categoria` non e' una stringa libera ma una FK a `core.categorie_articolo`. La categoria
scelta in create/update **deve appartenere allo stesso tenant** dell'articolo: il service lo
valida esplicitamente, altrimenti un client potrebbe linkare la categoria di un altro tenant
passando un id arbitrario (vedi sezione Tenant scoping).

### 4. Giacenza come campo semplice

`giacenza` e' un `NUMERIC` sull'articolo, aggiornato manualmente. Sufficiente per la demo e
per alimentare le righe bolla. Lo storico movimenti e la giacenza calcolata sono un modulo
Magazzino dedicato di fase 2.

---

## Data Model

### `core.categorie_articolo`

| Colonna     | Tipo         | Note                                  |
|-------------|--------------|---------------------------------------|
| id          | UUID PK      |                                       |
| tenant_id   | UUID FK      | → security.tenants (index)            |
| nome        | VARCHAR(100) | univoco per tenant                    |
| descrizione | VARCHAR(255) | nullable                              |
| is_active   | BOOLEAN      | default true                          |
| created_at  | TIMESTAMPTZ  |                                       |
| updated_at  | TIMESTAMPTZ  |                                       |

Vincolo: `UNIQUE(tenant_id, nome)`.

### `core.articoli`

| Colonna          | Tipo          | Note                                          |
|------------------|---------------|-----------------------------------------------|
| id               | UUID PK       |                                               |
| tenant_id        | UUID FK       | → security.tenants (index)                    |
| codice           | VARCHAR(50)   | SKU interno, univoco per tenant               |
| categoria_id     | UUID FK       | → core.categorie_articolo (nullable, index)   |
| descrizione      | VARCHAR(255)  |                                               |
| unita_misura     | VARCHAR(10)   | m² / pz / pallet / kg / scatola               |
| prezzo_unitario  | NUMERIC(12,4) | Decimal, ≥ 0                                   |
| aliquota_iva     | NUMERIC(5,2)  | es. 22.00 / 10.00 / 4.00                       |
| giacenza         | NUMERIC(12,3) | default 0                                      |
| codice_ean       | VARCHAR(14)   | barcode opzionale                             |
| note             | TEXT          | nullable                                      |
| is_active        | BOOLEAN       | default true (index)                          |
| version          | INTEGER       | default 1, optimistic locking                 |
| created_at       | TIMESTAMPTZ   |                                               |
| updated_at       | TIMESTAMPTZ   |                                               |

Vincolo: `UNIQUE(tenant_id, codice)`.

> Il `UNIQUE` composito `(tenant_id, codice)` e' tenant-critico: un unique globale su `codice`
> farebbe emergere conflitti 409 cross-tenant, leakando l'esistenza di codici di altri tenant.

---

## Tenant scoping

Replica del pattern Anagrafiche, con la regola di `00-llm-handoff.md`: il `tenant_id` non e'
mai un dato del payload, e' sempre `current_user.tenant_id`.

| Livello       | Enforcement                                                             |
|---------------|-------------------------------------------------------------------------|
| Model         | `tenant_id` FK obbligatoria + index su entrambe le tabelle              |
| Repository    | `_base_query(tenant_id)` filtra sempre `tenant_id` — ogni list/get scoped |
| get(tenant,id)| ritorna None se l'articolo e' di un altro tenant → 404                   |
| create        | `tenant_id` iniettato dalla sessione, mai dal payload                   |
| categoria_id  | validato nel tenant: la categoria deve esistere ed essere dello stesso tenant |
| Unicita'      | `UNIQUE(tenant_id, codice)` e `UNIQUE(tenant_id, nome)`                  |

---

## Permessi RBAC

| Permesso        | Descrizione                                         |
|-----------------|-----------------------------------------------------|
| articoli.read   | Lettura articoli e categorie del tenant             |
| articoli.write  | Creazione/modifica articoli e categorie             |
| articoli.delete | Disattivazione (soft delete) articolo               |

La gestione delle categorie ricade sotto `articoli.*` (e' amministrazione del catalogo): non
si introduce una terna `categorie.*` dedicata per non gonfiare il catalogo permessi.

### Assegnazione per ruolo

| Ruolo        | read | write | delete |
|--------------|------|-------|--------|
| admin        | ✓    | ✓     | ✓      |
| tenant_admin | ✓    | ✓     | ✓      |
| manager      | ✓    | ✓     |        |
| worker       | ✓    |       |        |
| user         | ✓    |       |        |

---

## Endpoint API

### Articoli

| Method | Path                       | Permesso        | Descrizione                       |
|--------|----------------------------|-----------------|-----------------------------------|
| GET    | /api/v1/articoli           | articoli.read   | Lista paginata con filtri         |
| POST   | /api/v1/articoli           | articoli.write  | Crea nuovo articolo               |
| GET    | /api/v1/articoli/{id}      | articoli.read   | Dettaglio singolo articolo        |
| PATCH  | /api/v1/articoli/{id}      | articoli.write  | Aggiorna articolo (richiede version) |
| DELETE | /api/v1/articoli/{id}      | articoli.delete | Soft delete (is_active = false)   |

### Categorie

| Method | Path                          | Permesso        | Descrizione                |
|--------|-------------------------------|-----------------|----------------------------|
| GET    | /api/v1/articoli/categorie    | articoli.read   | Lista categorie del tenant |
| POST   | /api/v1/articoli/categorie    | articoli.write  | Crea categoria             |
| PATCH  | /api/v1/articoli/categorie/{id} | articoli.write| Aggiorna categoria         |
| DELETE | /api/v1/articoli/categorie/{id} | articoli.delete | Disattiva categoria      |

### Filtri GET /articoli

- `categoria_id`: filtra per categoria
- `is_active`: bool (default true)
- `q`: ricerca testuale su codice / descrizione
- `skip` / `limit`: paginazione (default limit=50, max 200)

---

## Eventi e KPI

Su create/update/deactivate l'`ArticoloService` pubblica via `EventPublisher` sul canale
tenant-scoped:

- `articolo.created`
- `articolo.updated`
- `articolo.deactivated`

Il `DashboardService` espone un nuovo KPI "Articoli a catalogo" (conteggio articoli attivi del
tenant), cacheato in Redis e invalidato su `articolo.*`. Il frontend si iscrive all'evento e
fa auto-refresh del KPI, riusando il pattern `kpi.updated` gia' attivo.

---

## Convenzioni operative

- Tenant scoping obbligatorio: `tenant_id` sempre derivato dall'utente autenticato
- Soft delete: gli articoli non si cancellano fisicamente, si imposta `is_active = false`
- Disattivazione categoria con integrita' stretta: se esistono articoli **attivi** che la
  referenziano, la disattivazione e' **bloccata** con `409 Conflict` e il conteggio degli
  articoli coinvolti ("Categoria in uso da N articoli attivi: riassegnarli o disattivarli
  prima"). Cosi' nessun articolo attivo punta a una categoria archiviata.
- Validazione prezzo `≥ 0`, aliquota IVA in `{0, 4, 5, 10, 22}` (estendibile)
- Optimistic locking: ogni `PATCH` articolo richiede `version`, mismatch → 409
- SQL nei repository, logica nei service, schemi Pydantic espliciti, docstring IT, OpenAPI curato

---

## Aliquote IVA — valori supportati v1

| Aliquota | Uso tipico                          |
|----------|-------------------------------------|
| 22.00    | Aliquota ordinaria                  |
| 10.00    | Aliquota ridotta (alcune forniture) |
| 5.00     | Aliquota ridotta speciale           |
| 4.00     | Aliquota minima                     |
| 0.00     | Non imponibile / esente             |

---

## Unita' di misura — valori suggeriti

`m²`, `pz`, `pallet`, `kg`, `scatola`, `ml` (metro lineare), `cf` (confezione).

Campo libero `VARCHAR(10)` con suggerimenti frontend; nessuna tabella lookup nel v1.

---

## File previsti

| Layer      | File                                                                  |
|------------|-----------------------------------------------------------------------|
| Migration  | `alembic/versions/20260528_0012_add_articoli.py` (2 tabelle + permessi + role_permissions + seed demo) |
| Model      | `app/models/core/categoria_articolo.py`, `app/models/core/articolo.py`|
| Repository | `app/repositories/core/categoria_articolo_repository.py`, `app/repositories/core/articolo_repository.py` |
| Service    | `app/services/articoli/categoria_service.py`, `app/services/articoli/articolo_service.py` |
| Schemas    | `app/schemas/articoli/requests.py`, `app/schemas/articoli/responses.py` |
| Routes     | `app/api/v1/articoli/routes.py` (+ registrazione in `app/api/v1/router.py`) |
| Eventi     | publish nel service + nuovo KPI in `app/services/dashboard/dashboard_service.py` |
| Test       | `tests/test_articoli.py` (isolamento tenant, optimistic lock, categoria cross-tenant) |
| Frontend   | `ArticoliView.vue`, `ArticoloDetailView.vue`, gestione categorie, `services/articoli.js`, route, voce sidebar |

---

## Seed demo (migration)

Per il tenant `Ceramica Demo S.r.l.`:

- Categorie: `Pavimenti`, `Rivestimenti`, `Accessori posa`
- ~6 articoli realistici (es. "Gres porcellanato 60x60 grigio", `m²`, prezzo, IVA 22, categoria Pavimenti)

---

## Stato implementazione

- [x] Spec redatta
- [x] Migration 0012 tabelle articoli + categorie, permessi RBAC, seed demo
- [x] ORM models: Articolo, CategoriaArticolo
- [x] Repository: ArticoloRepository, CategoriaArticoloRepository
- [x] Service: ArticoloService (con optimistic lock + eventi), CategoriaService
- [x] Routes: /api/v1/articoli + /api/v1/articoli/categorie
- [x] KPI "Articoli a catalogo" in DashboardService
- [x] Test: isolamento tenant, optimistic lock, categoria cross-tenant (11 test, tutti verdi)
- [x] Frontend: ArticoliView (lista + filtri + modale + gestione categorie), ArticoloDetailView (con optimistic lock via version), service `articoli.js`, route `/articoli` + `/articoli/:id`, voce sidebar reale
- [x] Aggiornamento `struttura.md` (tenant scoping esteso al secondo dominio business)
