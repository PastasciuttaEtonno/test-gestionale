# Bolla Service

> 31 nodes · cohesion 0.16

## Key Concepts

- **BollaService** (38 connections) — `backend/app/services/bolle/bolla_service.py`
- **str** (21 connections) — `backend/app/services/bolle/bolla_service.py`
- **BollaResponse** (16 connections) — `backend/app/services/bolle/bolla_service.py`
- **Bolla** (11 connections) — `backend/app/services/bolle/bolla_service.py`
- **._get_or_404()** (11 connections) — `backend/app/services/bolle/bolla_service.py`
- **.add_riga()** (9 connections) — `backend/app/services/bolle/bolla_service.py`
- **._assert_bozza()** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **.create_bolla()** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **._notifica()** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **._ricalcola_e_salva()** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **.update_bolla()** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **.update_riga()** (8 connections) — `backend/app/services/bolle/bolla_service.py`
- **.delete_riga()** (7 connections) — `backend/app/services/bolle/bolla_service.py`
- **.annulla()** (6 connections) — `backend/app/services/bolle/bolla_service.py`
- **.emetti()** (6 connections) — `backend/app/services/bolle/bolla_service.py`
- **.delete_bolla()** (5 connections) — `backend/app/services/bolle/bolla_service.py`
- **.get_bolla()** (5 connections) — `backend/app/services/bolle/bolla_service.py`
- **._valida_anagrafica()** (5 connections) — `backend/app/services/bolle/bolla_service.py`
- **Aggiorna la testata di una bozza (optimistic locking via version).** (1 connections) — `backend/app/services/bolle/bolla_service.py`
- **Cancella una bozza (solo stato bozza).** (1 connections) — `backend/app/services/bolle/bolla_service.py`
- **Aggiunge una riga prendendo lo snapshot dei dati articolo.** (1 connections) — `backend/app/services/bolle/bolla_service.py`
- **Aggiorna la quantita' di una riga ricalcolando l'importo.** (1 connections) — `backend/app/services/bolle/bolla_service.py`
- **Rimuove una riga e ricalcola i totali.** (1 connections) — `backend/app/services/bolle/bolla_service.py`
- **Emette la bozza: consuma il numero dalla sequence e congela il documento.** (1 connections) — `backend/app/services/bolle/bolla_service.py`
- **Annulla una bolla emessa (stato terminale, resta a registro).** (1 connections) — `backend/app/services/bolle/bolla_service.py`
- *... and 6 more nodes in this community*

## Relationships

- [[Bolla Repository & Events]] (23 shared connections)
- [[Bolle Routes]] (10 shared connections)
- [[Articolo CRUD Methods]] (8 shared connections)
- [[Anagrafica Models]] (4 shared connections)
- [[Notifications & Events]] (4 shared connections)
- [[Articoli Schemas]] (2 shared connections)
- [[Community 39]] (2 shared connections)

## Source Files

- `backend/app/services/bolle/bolla_service.py`

## Audit Trail

- EXTRACTED: 156 (78%)
- INFERRED: 45 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*