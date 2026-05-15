# Backend Structure

## Struttura corrente

```text
backend/app/
  api/
  core/
  domain/
  models/
  repositories/
  schemas/
  services/
  main.py
```

## Regole per directory

### `api/`

- solo routing e dependency binding
- nessuna query SQL
- nessuna regola di business complessa

### `core/`

- configurazione runtime
- logging
- utility e policy di sicurezza

### `domain/`

- costanti
- enum
- eccezioni di dominio

### `models/`

- entita ORM SQLAlchemy

### `repositories/`

- accesso ai dati
- query persistenti

### `schemas/`

- request/response model Pydantic

### `services/`

- casi d'uso applicativi
- orchestrazione tra repository, policy e audit
