# API and OpenAPI Standards

## Regola obbligatoria

Ogni volta che si crea o modifica un endpoint FastAPI, la documentazione OpenAPI deve essere trattata come parte del codice.

## Requisiti minimi

- `Field(description="...")` su ogni attributo Pydantic
- `examples=[...]` per request e response
- docstring endpoint chiare e non generiche
- `responses={...}` espliciti nei decorator
- `summary=` esplicito quando utile
- tag coerenti per area funzionale
- firme tipizzate in modo completo

## Cosa evitare

- endpoint senza descrizione semantica
- schemi Pydantic senza documentazione campo per campo
- ritorni impliciti o ambigui
- eccezioni non tradotte in status code documentati

## Stato corrente

Gli endpoint attivi di `Auth`, `Users` e `Admin` sono allineati a questo standard e costituiscono la baseline da mantenere per ogni evoluzione futura.
