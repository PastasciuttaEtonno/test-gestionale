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
- stato utente inizializzato via endpoint `me`
- per il client auth corrente usare `axios` con interceptor request/response
- usare guardie `Vue Router` per UX, senza trattarle come autorizzazione definitiva
- se la fase richiede solo test auth, e accettabile `localStorage`; per fasi piu sensibili rivalutare storage e strategia token
