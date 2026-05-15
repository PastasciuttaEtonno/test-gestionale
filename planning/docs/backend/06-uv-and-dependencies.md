# UV and Dependencies

## Strumento scelto

`uv` e il gestore dipendenze Python del progetto.

## File di riferimento

- [backend/pyproject.toml](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/pyproject.toml)
- [backend/uv.lock](/c:/Users/ivan.lisciotto_webra/Desktop/project/backend/uv.lock)

## Regole operative

- le dipendenze si dichiarano in `pyproject.toml`
- il lockfile va aggiornato quando cambiano le dipendenze
- il container installa dipendenze da `uv.lock`
- non usare file `requirements.txt` come fonte primaria se il progetto usa `uv`
- prima di chiudere un aggiornamento dipendenze usare `uv lock --upgrade` e verificare la build Docker

## Stato corrente

- lockfile aggiornato all'ultima risoluzione disponibile al momento della fase corrente
- dipendenze backend installate nel container a partire da `uv.lock`
- la riproducibilita del backend dipende da:
  - tag immagine Python pin
  - versione `uv` pin
  - lockfile committato

## Comandi base

- `uv sync`
- `uv lock`
- `uv lock --upgrade`
- `uv run alembic upgrade head`
- `uv run uvicorn app.main:app --app-dir backend --reload`
