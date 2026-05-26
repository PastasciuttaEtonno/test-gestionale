# Modulo Anagrafiche

## Obiettivo

Primo modulo business tenant-aware del gestionale. Gestisce il registro centralizzato di
clienti, fornitori, agenti e altri soggetti economici con cui l'azienda cliente interagisce.

## Perimetro della v1

### In scope

- Anagrafica soggetto (persona fisica o giuridica)
- Tipo relazione: cliente, fornitore, cliente+fornitore, agente, altro
- Campi obbligatori fatturazione elettronica italiana (P.IVA, CF, codice SDI, PEC)
- Indirizzi multipli per anagrafica (legale, operativo, spedizione, fatturazione)
- CRUD completo con tenant scoping
- Filtri lista: tipo, attivo/disattivo, ricerca testuale

### Out of scope v1 (moduli futuri)

- Articoli / listino prezzi
- Conti bancari / IBAN
- Agenti con provvigioni
- Contatti secondari (referenti)
- Import da CSV / legacy

---

## Data Model

### `core.anagrafiche`

| Colonna          | Tipo          | Note                                          |
|------------------|---------------|-----------------------------------------------|
| id               | UUID PK       |                                               |
| tenant_id        | UUID FK       | → security.tenants                            |
| tipo             | VARCHAR(30)   | cliente / fornitore / cliente_fornitore / agente / altro |
| is_persona_fisica| BOOLEAN       | true = persona fisica, false = ente/società   |
| ragione_sociale  | VARCHAR(255)  | obbligatorio se is_persona_fisica = false     |
| cognome          | VARCHAR(150)  | obbligatorio se is_persona_fisica = true      |
| nome             | VARCHAR(150)  | if is_persona_fisica = true                   |
| partita_iva      | VARCHAR(16)   | nullable                                      |
| codice_fiscale   | VARCHAR(20)   | nullable                                      |
| codice_sdi       | VARCHAR(7)    | default "0000000" se si usa PEC               |
| pec              | VARCHAR(255)  | email certificata                             |
| regime_fiscale   | VARCHAR(10)   | es. RF01, RF19 (forfettario)                  |
| natura_giuridica | VARCHAR(50)   | es. SRL, SPA, DITTA_INDIVIDUALE               |
| email            | VARCHAR(255)  |                                               |
| telefono         | VARCHAR(32)   |                                               |
| website          | VARCHAR(255)  |                                               |
| note             | TEXT          |                                               |
| is_active        | BOOLEAN       | default true                                  |
| created_at       | TIMESTAMPTZ   |                                               |
| updated_at       | TIMESTAMPTZ   |                                               |

### `core.anagrafica_indirizzi`

| Colonna         | Tipo        | Note                                              |
|-----------------|-------------|---------------------------------------------------|
| id              | UUID PK     |                                                   |
| anagrafica_id   | UUID FK     | → core.anagrafiche, ondelete CASCADE              |
| tipo            | VARCHAR(30) | legale / operativo / spedizione / fatturazione    |
| is_principale   | BOOLEAN     | default false                                     |
| indirizzo       | VARCHAR(255)|                                                   |
| citta           | VARCHAR(120)|                                                   |
| cap             | VARCHAR(10) |                                                   |
| provincia       | VARCHAR(4)  | sigla italiana o equivalente estero               |
| paese           | VARCHAR(2)  | ISO 3166-1 alpha-2, default "IT"                  |
| created_at      | TIMESTAMPTZ |                                                   |
| updated_at      | TIMESTAMPTZ |                                                   |

---

## Permessi RBAC

| Permesso            | Descrizione                                      |
|---------------------|--------------------------------------------------|
| anagrafiche.read    | Lettura anagrafiche del tenant                   |
| anagrafiche.write   | Creazione e modifica anagrafiche                 |
| anagrafiche.delete  | Disattivazione (soft delete) anagrafica          |

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

| Method | Path                           | Permesso            | Descrizione                            |
|--------|--------------------------------|---------------------|----------------------------------------|
| GET    | /api/v1/anagrafiche            | anagrafiche.read    | Lista paginata con filtri              |
| POST   | /api/v1/anagrafiche            | anagrafiche.write   | Crea nuova anagrafica con indirizzi    |
| GET    | /api/v1/anagrafiche/{id}       | anagrafiche.read    | Dettaglio singola anagrafica           |
| PATCH  | /api/v1/anagrafiche/{id}       | anagrafiche.write   | Aggiorna anagrafica                    |
| DELETE | /api/v1/anagrafiche/{id}       | anagrafiche.delete  | Soft delete (is_active = false)        |
| GET    | /api/v1/anagrafiche/{id}/indirizzi | anagrafiche.read | Lista indirizzi                       |
| POST   | /api/v1/anagrafiche/{id}/indirizzi | anagrafiche.write| Aggiunge indirizzo                   |
| PATCH  | /api/v1/anagrafiche/{id}/indirizzi/{addr_id} | anagrafiche.write | Modifica indirizzo    |
| DELETE | /api/v1/anagrafiche/{id}/indirizzi/{addr_id} | anagrafiche.write | Rimuove indirizzo     |

### Filtri GET /anagrafiche

- `tipo`: cliente | fornitore | cliente_fornitore | agente | altro
- `is_active`: bool (default true)
- `q`: ricerca testuale su ragione_sociale / cognome+nome / P.IVA / CF
- `skip` / `limit`: paginazione (default limit=50)

---

## Convenzioni operative

- Tenant scoping obbligatorio: `tenant_id` sempre derivato dall'utente autenticato
- Soft delete: non si cancellano fisicamente le anagrafiche, si imposta `is_active = false`
- `display_name`: campo calcolato restituito dall'API = ragione_sociale se giuridica,
  altrimenti cognome + nome
- Validazione: se `is_persona_fisica = false`, `ragione_sociale` obbligatorio;
  se `true`, almeno `cognome` obbligatorio
- Codice SDI: se assente e PEC presente → "0000000"; validazione formato 7 char alfanumerico

---

## Regime fiscale — valori supportati

| Codice | Descrizione                    |
|--------|--------------------------------|
| RF01   | Ordinario                      |
| RF02   | Contribuenti minimi            |
| RF04   | Agricoltura e attività connesse|
| RF10   | Commercio elettronico          |
| RF17   | Vendita sali e tabacchi        |
| RF18   | IVA per cassa (art. 32-bis)   |
| RF19   | Regime forfettario             |

---

## Stato implementazione

- [x] Spec redatta
- [x] Migration 0009 permessi RBAC anagrafiche
- [x] Migration 0010 tabelle anagrafiche e indirizzi con seed demo
- [x] ORM models: Anagrafica, AnagraficaIndirizzo
- [x] Repository: AnagraficaRepository
- [x] Service: AnagraficaService
- [x] Routes: /api/v1/anagrafiche
- [x] Frontend: AnagraficheView (lista + modale create/edit)
