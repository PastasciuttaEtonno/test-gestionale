# Skill: Backend Auth

## Obiettivo

Trattare `Auth & Identity` come modulo trasversale di piattaforma.

## Regole

- ruoli e permessi non hardcoded ovunque
- audit sempre considerato
- utente applicativo separato dal profilo anagrafico
- token, sessioni e hashing isolati in `core/security` e `services/auth`
- il `tenant_id` va sempre derivato dal profilo autenticato, mai passato come fonte di verita dal client
- i segreti di configurazione tenant non devono essere restituiti in chiaro

## Priorità

1. persistenza utenti e ruoli
2. hashing password
3. JWT reali
4. refresh token revocabili
5. audit reale su DB
