# Skill: Frontend General

## Obiettivo

Preparare un frontend gestionale coerente con API sicure e contratti stabili.

## Regole

- usare schemi API chiari come contratto
- centralizzare auth client-side
- evitare logica autorizzativa come unica fonte di verita
- trattare tabelle, form e filtri come componenti riusabili

## Integrazione con backend

- bearer token tramite client HTTP centralizzato
- refresh token gestito in un solo punto
- stato utente inizializzato via refresh di sessione e profilo restituito dal backend
- per il client auth corrente usare `axios` con interceptor request/response
- usare guardie `Vue Router` per UX, senza trattarle come autorizzazione definitiva
- quando il frontend smette di essere solo demo, preferire `access token` in memoria e `refresh token` in cookie `HttpOnly`
