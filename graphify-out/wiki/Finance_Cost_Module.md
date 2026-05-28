# Finance Cost Module

> 36 nodes · cohesion 0.09

## Key Concepts

- **FinanceCostEntry** (13 connections) — `backend/app/models/core/finance_cost_entry.py`
- **FinanceService** (13 connections) — `backend/app/services/finance/finance_service.py`
- **FinanceCostRepository** (12 connections) — `backend/app/repositories/core/finance_cost_repository.py`
- **.create_cost()** (6 connections) — `backend/app/services/finance/finance_service.py`
- **create_finance_cost()** (6 connections) — `backend/app/api/v1/finance/routes.py`
- **CurrentUserResponse** (5 connections) — `backend/app/services/finance/finance_service.py`
- **._validate_tenant_scope()** (5 connections) — `backend/app/services/finance/finance_service.py`
- **routes.py** (4 connections) — `backend/app/api/v1/finance/routes.py`
- **CreateFinanceCostRequest** (4 connections) — `backend/app/services/finance/finance_service.py`
- **FinanceCostResponse** (4 connections) — `backend/app/services/finance/finance_service.py`
- **Session** (4 connections) — `backend/app/services/finance/finance_service.py`
- **str** (4 connections) — `backend/app/services/finance/finance_service.py`
- **get_finance_service()** (4 connections) — `backend/app/api/v1/finance/routes.py`
- **FinanceService** (4 connections) — `backend/app/api/v1/finance/routes.py`
- **CreateFinanceCostRequest** (3 connections) — `backend/app/api/v1/finance/routes.py`
- **CurrentUserResponse** (3 connections) — `backend/app/api/v1/finance/routes.py`
- **FinanceCostResponse** (3 connections) — `backend/app/api/v1/finance/routes.py`
- **Session** (3 connections) — `backend/app/api/v1/finance/routes.py`
- **finance_service.py** (3 connections) — `backend/app/services/finance/finance_service.py`
- **.create()** (3 connections) — `backend/app/repositories/core/finance_cost_repository.py`
- **.__init__()** (3 connections) — `backend/app/services/finance/finance_service.py`
- **finance_cost_repository.py** (2 connections) — `backend/app/repositories/core/finance_cost_repository.py`
- **Session** (2 connections) — `backend/app/repositories/core/finance_cost_repository.py`
- **.__init__()** (2 connections) — `backend/app/repositories/core/finance_cost_repository.py`
- **FinanceCostEntry** (2 connections) — `backend/app/repositories/core/finance_cost_repository.py`
- *... and 11 more nodes in this community*

## Relationships

- [[Tenant Settings & Dashboard]] (7 shared connections)
- [[Articoli Services]] (5 shared connections)
- [[Community 42]] (2 shared connections)
- [[Articoli Schemas]] (1 shared connections)
- [[Community 67]] (1 shared connections)

## Source Files

- `backend/app/api/v1/finance/routes.py`
- `backend/app/models/core/finance_cost_entry.py`
- `backend/app/repositories/core/finance_cost_repository.py`
- `backend/app/services/finance/finance_service.py`

## Audit Trail

- EXTRACTED: 74 (58%)
- INFERRED: 54 (42%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [[index]] to navigate.*