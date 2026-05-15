# Skill: Backend FastAPI

## Regole endpoint

- route tipizzate completamente
- `response_model` sempre esplicito
- `status_code` esplicito
- `responses={...}` sempre definito
- docstring con azione e vincoli
- tag coerente per dominio

## Dependency injection

- autenticazione via dependency
- autorizzazione via dependency o policy
- nessun accesso globale implicito a stato condiviso
