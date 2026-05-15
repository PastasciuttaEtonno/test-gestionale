# Skill: OpenAPI and Swagger Standard

## Regola obbligatoria

Ogni endpoint backend FastAPI deve produrre documentazione automatica pulita e leggibile.

## Checklist

- `Field(description="...")` su tutti i campi Pydantic
- `examples=[...]` sui campi principali
- docstring endpoint con azione e vincoli
- `response_model` esplicito
- `status_code` esplicito
- `responses={...}` esplicito
- `tags` coerenti
- firme con type hints completi

## Obiettivo

Swagger non e un effetto collaterale: e parte della qualità dell'API.
