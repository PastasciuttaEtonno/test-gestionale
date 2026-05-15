# Skill: Docker and UV Workflow

## Regole

- dipendenze gestite con `uv`
- container costruiti da `uv.lock`
- `docker compose` usato per smoke test end-to-end

## Workflow base

1. aggiornare `pyproject.toml`
2. rigenerare `uv.lock`
3. verificare `uv run ...` localmente
4. verificare `docker compose up --build`

## Obiettivo

Evitare divergenza tra ambiente locale Python e ambiente container.
