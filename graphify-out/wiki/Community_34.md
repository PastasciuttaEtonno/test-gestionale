# Community 34

> 19 nodes · cohesion 0.13

## Key Concepts

- **Bolla** (7 connections) — `backend/app/repositories/core/bolla_repository.py`
- **str** (7 connections) — `backend/app/repositories/core/bolla_repository.py`
- **.list()** (6 connections) — `backend/app/repositories/core/bolla_repository.py`
- **.get()** (5 connections) — `backend/app/repositories/core/bolla_repository.py`
- **int** (4 connections) — `backend/app/repositories/core/bolla_repository.py`
- **._base_query()** (4 connections) — `backend/app/repositories/core/bolla_repository.py`
- **.count_emesse_nel_mese()** (4 connections) — `backend/app/repositories/core/bolla_repository.py`
- **.lock_document_sequence()** (4 connections) — `backend/app/repositories/core/bolla_repository.py`
- **TenantDocumentSequence** (3 connections) — `backend/app/repositories/core/bolla_repository.py`
- **.create()** (3 connections) — `backend/app/repositories/core/bolla_repository.py`
- **.delete()** (3 connections) — `backend/app/repositories/core/bolla_repository.py`
- **.update()** (3 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Restituisce bolle filtrate e il totale.** (1 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Restituisce una singola bolla del tenant con le righe.** (1 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Persiste una nuova bolla (e le sue righe).** (1 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Aggiorna una bolla esistente.** (1 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Rimuove fisicamente una bolla (usato solo per le bozze).** (1 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Conta le bolle emesse del tenant nel mese corrente (per il KPI).** (1 connections) — `backend/app/repositories/core/bolla_repository.py`
- **Restituisce la sequence con lock di riga (FOR UPDATE) per numerazione safe.** (1 connections) — `backend/app/repositories/core/bolla_repository.py`

## Relationships

- [[Bolla Repository & Events]] (12 shared connections)
- [[Tenant Encryption & Sequences]] (4 shared connections)

## Source Files

- `backend/app/repositories/core/bolla_repository.py`

## Audit Trail

- EXTRACTED: 52 (87%)
- INFERRED: 8 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*