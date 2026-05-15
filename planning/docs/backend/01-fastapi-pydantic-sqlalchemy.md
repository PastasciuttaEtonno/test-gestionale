# FastAPI, Pydantic, SQLAlchemy

## FastAPI

FastAPI e il layer HTTP del progetto:

- routing
- dependency injection
- generazione OpenAPI
- validazione request/response tramite Pydantic

Non deve ospitare logica di business o query dirette.

## Pydantic

Pydantic definisce i contratti applicativi:

- input degli endpoint
- output degli endpoint
- serializzazione consistente
- descrizioni OpenAPI

Uso obbligatorio:

- `Field(description="...")`
- `examples=[...]`
- type hints coerenti

## SQLAlchemy

SQLAlchemy e il layer ORM:

- modelli persistenti
- mapping su PostgreSQL
- base per repository e sessioni DB

Regola:

gli oggetti ORM non devono essere restituiti direttamente dall'API. Gli endpoint espongono solo schemi Pydantic.

## Nota sul tenant scoping

Quando un endpoint opera nel perimetro `tenant_admin`:

- il filtro tenant va applicato nel service o nel repository dedicato
- il frontend non deve essere considerato fonte affidabile per il `tenant_id`
- il `tenant_id` va sempre risolto dal profilo autenticato corrente
