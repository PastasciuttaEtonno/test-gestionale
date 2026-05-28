# Modulo Bolle / DDT

## Obiettivo

Terzo modulo business e **primo documento composito** del gestionale: il Documento di
Trasporto (DDT, "bolla"). Lega Anagrafiche (destinatario) e Articoli (righe) in un documento
numerato progressivamente, ed e' il ponte verso il modulo Fatture.

E' costruito sugli stessi layer di Anagrafiche/Articoli (model -> repository -> service ->
routes) e riusa tenant scoping, optimistic locking, eventi SSE e soft-delete gia' validati.

## Perimetro della v1

### In scope

- Testata DDT con destinatario (anagrafica), data, causale trasporto e campi logistici
- Righe documento con **snapshot** dei dati articolo (codice/descrizione/prezzo/IVA congelati)
- Ciclo di vita **bozza -> emessa -> annullata**
- Numerazione progressiva consumata dalla sequence `delivery_note_italy` solo all'emissione
- Totali (imponibile, IVA, totale) calcolati dalle righe
- Immutabilita' delle bolle emesse (solo annullabili)
- Optimistic locking sulla testata (`version`)
- Eventi SSE su create/emit/annulla + KPI dashboard "Bolle del mese"
- Filtri lista: stato, anagrafica, ricerca su numero

### Out of scope v1 (moduli futuri)

- Trasformazione bolla -> fattura (modulo Fatture)
- Generazione PDF del DDT
- Stampa/invio via email
- Scarico automatico di magazzino sulle righe
- Bolle di acquisto / reso da fornitore con logica dedicata
- Numerazioni multiple selezionabili dall'utente (si usa la sequence DDT predefinita)

---

## Decisioni di design

### 1. Ciclo di vita: bozza -> emessa -> annullata

La bolla nasce come **bozza** (`stato = "bozza"`), liberamente editabile (testata e righe).
All'**emissione** (`POST /bolle/{id}/emetti`) il sistema consuma il numero dalla sequence e
passa a `stato = "emessa"`. Una bolla emessa e' **immutabile**: si puo' solo **annullare**
(`stato = "annullata"`), mai modificarne righe o totali. Le bozze scartate possono essere
cancellate senza bruciare numeri.

### 2. Snapshot dei dati articolo nelle righe

Quando un articolo viene aggiunto a una bolla, i suoi dati (`codice`, `descrizione`,
`prezzo_unitario`, `aliquota_iva`, `unita_misura`) vengono **copiati** nella riga. Il documento
resta immutabile anche se l'articolo cambia prezzo o descrizione in seguito. Requisito fiscale:
un DDT gia' emesso non deve mutare retroattivamente. La riga mantiene comunque `articolo_id`
come riferimento (nullable, per righe libere future), ma i valori stampati sono lo snapshot.

### 3. Numerazione concorrenza-safe

All'emissione si legge la riga `tenant_document_sequences` con `sequence_code =
"delivery_note_italy"` usando un lock di riga (`SELECT ... FOR UPDATE`), si costruisce il numero
(`prefix` + `next_number`, es. `BL4441`), si incrementa `next_number` e si committa nella stessa
transazione dell'emissione. Il lock evita numeri duplicati sotto emissioni concorrenti.

### 4. Totali calcolati, mai inviati dal client

`totale_imponibile`, `totale_iva` e `totale` sono calcolati dal service sommando le righe; il
client non li invia mai. Ricalcolati a ogni modifica delle righe (solo in stato bozza). Importi
in `NUMERIC` (Decimal), coerente con Articoli.

---

## Data Model

### `core.bolle`

| Colonna             | Tipo          | Note                                                  |
|---------------------|---------------|-------------------------------------------------------|
| id                  | UUID PK       |                                                       |
| tenant_id           | UUID FK       | -> security.tenants (index)                           |
| numero              | VARCHAR(40)   | nullable finche' bozza; valorizzato all'emissione     |
| anno                | INTEGER       | nullable; anno di emissione                           |
| stato               | VARCHAR(20)   | bozza / emessa / annullata (index)                    |
| data_documento      | DATE          | data del DDT                                          |
| anagrafica_id       | UUID FK       | -> core.anagrafiche (destinatario), index             |
| causale_trasporto   | VARCHAR(50)   | vendita / conto_visione / reso / riparazione / omaggio|
| aspetto_beni        | VARCHAR(60)   | es. "Scatole", "Pallet", "A vista"                    |
| num_colli           | INTEGER       | nullable                                              |
| peso_kg             | NUMERIC(10,3) | nullable                                              |
| trasporto_a_cura    | VARCHAR(20)   | mittente / destinatario / vettore                     |
| vettore             | VARCHAR(120)  | nullable                                               |
| note                | TEXT          | nullable                                              |
| totale_imponibile   | NUMERIC(14,2) | calcolato dalle righe                                 |
| totale_iva          | NUMERIC(14,2) | calcolato dalle righe                                 |
| totale              | NUMERIC(14,2) | imponibile + iva                                      |
| is_active           | BOOLEAN       | default true (soft delete bozze)                      |
| version             | INTEGER       | default 1, optimistic locking                         |
| created_at          | TIMESTAMPTZ   |                                                       |
| updated_at          | TIMESTAMPTZ   |                                                       |

Vincolo: `UNIQUE(tenant_id, numero)` (parziale: solo quando `numero IS NOT NULL`).

### `core.bolle_righe`

| Colonna           | Tipo          | Note                                            |
|-------------------|---------------|-------------------------------------------------|
| id                | UUID PK       |                                                 |
| bolla_id          | UUID FK       | -> core.bolle, ondelete CASCADE (index)         |
| articolo_id       | UUID FK       | -> core.articoli (nullable, riferimento)        |
| codice_articolo   | VARCHAR(50)   | snapshot                                         |
| descrizione       | VARCHAR(255)  | snapshot                                         |
| unita_misura      | VARCHAR(10)   | snapshot                                         |
| quantita          | NUMERIC(12,3) | > 0                                             |
| prezzo_unitario   | NUMERIC(12,4) | snapshot                                         |
| aliquota_iva      | NUMERIC(5,2)  | snapshot                                         |
| importo_riga      | NUMERIC(14,2) | calcolato: quantita * prezzo_unitario           |
| ordine            | INTEGER       | posizione della riga nel documento              |

---

## Tenant scoping

Replica del pattern Anagrafiche/Articoli, regola di `00-llm-handoff.md`: `tenant_id` sempre da
`current_user`, mai dal payload.

| Livello        | Enforcement                                                              |
|----------------|--------------------------------------------------------------------------|
| Model          | `tenant_id` FK + index sulla testata                                     |
| Repository     | `_base_query(tenant_id)` filtra sempre il tenant; le righe si leggono solo via bolla del tenant |
| anagrafica_id  | validata nel tenant: il destinatario deve appartenere allo stesso tenant |
| articolo_id    | validato nel tenant prima dello snapshot                                 |
| numero         | la sequence consumata e' quella del tenant (scoped su tenant_id)         |

---

## Ciclo di vita e numerazione

```
            POST /bolle                 POST /bolle/{id}/emetti        POST /bolle/{id}/annulla
   (vuoto) ─────────────▶  BOZZA  ─────────────────────────────▶  EMESSA  ─────────────────▶  ANNULLATA
                            │  ▲                                     │
              PATCH testata │  │ PATCH/POST/DELETE righe             │ (immutabile: solo annulla)
                            ▼  │                                     ▼
                          (editabile)                          (numero assegnato,
                                                                righe congelate)
```

- **bozza**: testata e righe modificabili; `numero` NULL; totali ricalcolati a ogni modifica
- **emessa**: numero consumato dalla sequence; righe/totali congelati; non modificabile
- **annullata**: stato terminale; resta a registro per tracciabilita' (no cancellazione fisica)

Emissione: richiede almeno una riga e un destinatario valido. Consuma `delivery_note_italy`
con lock di riga.

---

## Permessi RBAC

| Permesso      | Descrizione                                                  |
|---------------|--------------------------------------------------------------|
| bolle.read    | Lettura bolle e righe del tenant                             |
| bolle.write   | Creazione/modifica bozze, gestione righe, **emissione**      |
| bolle.delete  | Cancellazione bozze e **annullamento** bolle emesse          |

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

### Testata

| Method | Path                       | Permesso     | Descrizione                            |
|--------|----------------------------|--------------|----------------------------------------|
| GET    | /api/v1/bolle              | bolle.read   | Lista paginata con filtri              |
| POST   | /api/v1/bolle              | bolle.write  | Crea bozza                             |
| GET    | /api/v1/bolle/{id}         | bolle.read   | Dettaglio testata + righe              |
| PATCH  | /api/v1/bolle/{id}         | bolle.write  | Modifica testata bozza (richiede version) |
| DELETE | /api/v1/bolle/{id}         | bolle.delete | Cancella bozza (solo stato bozza)      |
| POST   | /api/v1/bolle/{id}/emetti  | bolle.write  | Emette la bozza: consuma numero, stato=emessa |
| POST   | /api/v1/bolle/{id}/annulla | bolle.delete | Annulla una bolla emessa               |

### Righe (solo su bozza)

| Method | Path                                  | Permesso    | Descrizione        |
|--------|---------------------------------------|-------------|--------------------|
| POST   | /api/v1/bolle/{id}/righe              | bolle.write | Aggiunge una riga  |
| PATCH  | /api/v1/bolle/{id}/righe/{riga_id}    | bolle.write | Modifica una riga  |
| DELETE | /api/v1/bolle/{id}/righe/{riga_id}    | bolle.write | Rimuove una riga   |

### Filtri GET /bolle

- `stato`: bozza | emessa | annullata
- `anagrafica_id`: filtra per destinatario
- `q`: ricerca sul numero documento
- `skip` / `limit`: paginazione (default 50, max 200)

---

## Eventi e KPI

Su create/emit/annulla l'`BollaService` pubblica via `EventPublisher` sul canale tenant:

- `bolla.created`
- `bolla.emessa`
- `bolla.annullata`

Nuovo KPI dashboard "Bolle emesse nel mese" (conteggio bolle `emessa` del tenant nel mese
corrente), cacheato in Redis e invalidato sugli eventi `bolla.*`.

---

## Convenzioni operative

- Tenant scoping obbligatorio: `tenant_id` da utente autenticato
- Le righe si modificano solo in stato bozza; tentativi su bolle emesse -> 409
- Snapshot articolo immutabile: la riga non rilegge mai i dati correnti dell'articolo
- Totali calcolati dal service, mai dal client
- Optimistic locking: `PATCH /bolle/{id}` richiede `version`, mismatch -> 409
- Emissione idempotente-safe: ri-emettere una bolla gia' emessa -> 409
- Numerazione concorrenza-safe con lock di riga sulla sequence
- SQL nei repository, logica nei service, schemi Pydantic espliciti, docstring IT, OpenAPI curato

---

## Causali di trasporto e valori supportati

| Causale        | Uso                                  |
|----------------|--------------------------------------|
| vendita        | Consegna merce venduta               |
| conto_visione  | Merce in visione presso il cliente   |
| reso           | Reso da cliente                      |
| riparazione    | Invio/ritorno per riparazione        |
| omaggio        | Omaggio / campionatura               |

Trasporto a cura di: `mittente` | `destinatario` | `vettore`.
Aspetto dei beni: campo libero con suggerimenti (`Scatole`, `Pallet`, `A vista`, `Sfuso`).

---

## File previsti

| Layer      | File                                                                  |
|------------|-----------------------------------------------------------------------|
| Migration  | `alembic/versions/20260529_0013_add_bolle.py` (2 tabelle + permessi + role_permissions + seed demo) |
| Model      | `app/models/core/bolla.py`, `app/models/core/bolla_riga.py`           |
| Repository | `app/repositories/core/bolla_repository.py`                           |
| Service    | `app/services/bolle/bolla_service.py` (lifecycle, numerazione, totali, eventi) |
| Schemas    | `app/schemas/bolle/requests.py`, `app/schemas/bolle/responses.py`     |
| Routes     | `app/api/v1/bolle/routes.py` (+ registrazione in `app/api/v1/router.py`) |
| Eventi     | publish nel service + nuovo KPI in `app/services/dashboard/dashboard_service.py` |
| Test       | `tests/test_bolle.py` (isolamento tenant, lifecycle, snapshot, numerazione, immutabilita', optimistic lock) |
| Frontend   | `BolleView.vue` (lista), `BollaDetailView.vue` (testata + righe + emetti/annulla), `services/bolle.js`, route, voce sidebar |
| Doc        | questo file + update `current-state.md`, `00-llm-handoff.md`, `struttura.md` |

---

## Seed demo (migration)

Per il tenant `Ceramica Demo S.r.l.`, usando articoli e anagrafiche gia' seedati:

- 1 bolla **emessa** (numero `BL4441`) verso "Edilceram S.r.l." con 2 righe (gres + colla)
- 1 bolla **bozza** verso "Costruzioni Bianchi S.p.A." con 1 riga
- la sequence `delivery_note_italy` parte da `next_number = 4441` (gia' seedata); la bolla emessa nel seed la porta a 4442

---

## Stato implementazione

- [x] Spec redatta
- [x] Migration 0013 tabelle bolle + righe, permessi RBAC, seed demo (1 emessa BL4441 + 1 bozza)
- [x] ORM models: Bolla, BollaRiga (snapshot righe, relazione cascade)
- [x] Repository: BollaRepository (scoped, lock sequence FOR UPDATE)
- [x] Service: BollaService (lifecycle, numerazione concorrenza-safe, totali, eventi)
- [x] Routes: /api/v1/bolle + righe + emetti/annulla
- [x] KPI "Bolle emesse nel mese" in DashboardService
- [x] Test: isolamento tenant, lifecycle, snapshot, numerazione, immutabilita', optimistic lock (14 test)
- [x] Frontend: BolleView (lista + crea bozza), BollaDetailView (composizione righe + emetti/annulla), service, route, sidebar
- [x] Aggiornamento `struttura.md`, `current-state.md`, `00-llm-handoff.md`

## Note implementative

- Le righe sono gestite via collezione ORM in-memory (`bolla.righe.append/remove`), non con
  query separate: evita il bug del ricalcolo totali su collezione stantia ricaricata
  dall'identity-map dopo un flush.
- Smoke test live verificato: create bozza -> add/update riga (totali corretti) -> emetti
  (numero progressivo da sequence) -> 409 su modifica emessa -> annulla; KPI aggiornato.
