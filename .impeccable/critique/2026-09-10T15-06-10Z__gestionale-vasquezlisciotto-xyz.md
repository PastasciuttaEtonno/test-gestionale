---
target: gestionale (stack Docker locale, post P1+P2)
total_score: 27
p0_count: 0
p1_count: 1
timestamp: 2026-09-10T15-06-10Z
slug: gestionale-vasquezlisciotto-xyz
---
## Design Health Score

| # | Euristica | Voto | Δ | Problema chiave residuo |
|---|-----------|------|---|-------------------------|
| 1 | Visibilità dello stato | 3 | = | Il blocco demo si annuncia tre volte insieme (banner, riquadro nel form, toast); nessuno skeleton in caricamento |
| 2 | Corrispondenza col mondo reale | 3 | +1 | Resta "IN ARRIVO (V2)" con il numero di versione interno, e "SMTP" come etichetta KPI |
| 3 | Controllo e libertà | 3 | = | Nessun undo; il banner demo non è chiudibile; il pannello notifiche non si chiude al cambio rotta |
| 4 | Coerenza e standard | 3 | +1 | Tre formati di valuta ancora in circolazione; "Logout" vs "Esci"; modifica via modale su una lista, via rotta sull'altra |
| 5 | Prevenzione degli errori | 3 | +1 | Nessuna validazione inline; "Salva" resta attivo in sola lettura |
| 6 | Riconoscere invece che ricordare | 3 | +1 | Nessuna cronologia dei documenti aperti di recente |
| 7 | Flessibilità ed efficienza | 2 | +1 | Nessuna scorciatoia, nessun ordinamento colonne, nessuna paginazione, nessuna selezione multipla |
| 8 | Design estetico e minimale | 3 | +1 | KPI annidati in un pannello (6 card dentro card); il riquadro roadmap occupa stabilmente la colonna destra |
| 9 | Recupero dagli errori | 2 | = | Il messaggio demo triplicato resta il caso peggiore; nessun errore a livello di campo |
| 10 | Aiuto e documentazione | 2 | +1 | Aiuti solo sui campi fiscali; empty state che non insegnano; la riga di assistenza nel login sembra un link e non lo è |
| **Totale** | | **27/40** | **+7** | **Acceptable, limite superiore** |

## Anti-Patterns Verdict

**Valutazione LLM.** Il difetto dominante della prima passata è chiuso. L'app non applica più un unico gesto tipografico a 96 punti diversi, e la dashboard non mostra più all'utente la propria impalcatura. Quello che resta non è più questione di gusto ma di funzioni mancanti: ordinamento, paginazione, scorciatoie, validazione. È un cambio di categoria del problema.

**Scansione deterministica.** Il detector bundled resta assente (`scripts/detector/detect-antipatterns.mjs`): scansione CLI non disponibile, come nella prima esecuzione. Sostituita con misure nel browser sullo stack Docker locale, su cinque viste autenticate con dati reali.

| Misura | Prima | Ora |
|---|---|---|
| Testi sotto la soglia di contrasto | 3 tipi su 4 viste | **0 su 5 viste** |
| Controlli senza nome accessibile | 3 pulsanti + 55 campi + ricerche | **0** |
| `<th>` senza `scope` | 49 | **0** |
| Etichette maiuscolo spaziato | 96 | **4** |
| Colori fuori sistema (`emerald`/`amber`/`blue`/`violet`) | 15 usi | **0** |
| Gradienti sul rosso brand | 2 | 1 (solo il pannello del login) |
| Righe di tabella raggiungibili da tastiera | 0 | **tutte** |
| Gergo tecnico nelle viste principali | 8 stringhe | **0** |
| `<title>` distinti per rotta | 1 per tutta l'app | **11** |

**Overlay visivi.** Non disponibili: senza detector bundled non è stato iniettato nulla nella pagina. In compenso questa esecuzione ha misurato l'app vera in Docker con dati di database, non un banco di prova.

## Overall Impression

L'app ora si comporta come lo strumento che PRODUCT.md descrive. Il colore dice una cosa sola e la dice ovunque allo stesso modo; la tipografia non affatica; la dashboard apre sul lavoro invece che sulla propria architettura.

Il baricentro dei problemi si è spostato. Prima era "questa interfaccia è confusa da leggere". Ora è "questa interfaccia si legge bene ma non si lascia guidare": non c'è modo di ordinare una colonna, paginare un elenco lungo, selezionare più righe o muoversi con la tastiera oltre al tab. Per l'utente che arriva da un gestionale desktop, questa è la distanza che resta.

L'occasione più grande: **rendere le tabelle governabili** — ordinamento, paginazione, selezione multipla, una scorciatoia per la ricerca.

## What's Working

1. **La scala di stato regge su tutte le viste.** Sei stati che in dashboard erano sei pillole identiche ora si separano in quattro gradi leggibili, con lo stesso significato su `/bolle` e sulle schede. Il glifo li tiene distinguibili anche in scala di grigi.
2. **I form sono programmaticamente corretti.** 55 campi con label collegata, `aria-required` sugli obbligatori e il formato atteso su P.IVA, CF, SDI, PEC e EAN. Il fatto che PrimeVue Select richiedesse `aria-labelledby` invece di `for` è gestito dentro `CampoForm`, quindi le viste non possono più sbagliarlo.
3. **La dashboard parla italiano da ufficio.** Nessuna occorrenza di Celery, Redis, SSE, UUID o codici permesso su nessuna delle viste principali.

## Priority Issues

### [P1] Le tabelle non si governano

**Cosa.** Nessuna colonna è ordinabile, nessun elenco è paginato, non esiste selezione multipla, non c'è nessuna scorciatoia da tastiera in tutta l'app. Le righe ora si aprono da tastiera, ma è l'unica cosa che si può fare da tastiera.

**Perché conta.** PRODUCT.md descrive utenti che arrivano da un desktop VB6 e "expect dense forms, predictable layouts, keyboard flow". Con sei righe di demo non si vede; con duemila anagrafiche l'elenco diventa inutilizzabile.

**Fix.** Header ordinabili con `aria-sort`, paginazione o scroll virtuale sopra le ~100 righe, selezione con checkbox e azioni massive, `/` per la ricerca e `n` per il nuovo documento.

**Comando suggerito.** `impeccable harden`

### [P2] Il blocco in modalità demo si annuncia tre volte

**Cosa.** Premendo Salva l'utente riceve simultaneamente il banner persistente in alto, un riquadro rosso dentro il form e un toast in basso, tutti con lo stesso testo. E il pulsante Salva resta primario e attivo pur non potendo salvare.

**Perché conta.** È il momento in cui l'utente ha appena finito di compilare: tre messaggi identici leggono come tre errori diversi.

**Fix.** Un solo canale: disattivare i pulsanti di scrittura in sola lettura con la spiegazione accanto, e togliere toast e riquadro.

**Comando suggerito.** `impeccable clarify`

### [P2] I formati dei dati non sono uniformi

**Cosa.** Tre formati di valuta ancora presenti (`12.480,00 EUR` in dashboard, `14,20 €` in articoli, `1301,74 €` in bolle), "Logout" a desktop e "Esci" a 390px, valore vuoto reso `-` in un punto e `— bozza` in un altro.

**Perché conta.** Sono i dati che l'operatore confronta a colpo d'occhio. Tre notazioni per un importo costringono a rileggere.

**Fix.** Un unico helper `Intl.NumberFormat("it-IT", { style: "currency", currency: "EUR" })` per tutti gli importi, un solo verbo per l'uscita, un solo segnaposto per il vuoto.

**Comando suggerito.** `impeccable polish`

### [P2] Niente validazione a livello di campo

**Cosa.** P.IVA, Codice Fiscale, SDI e PEC hanno ora il formato atteso scritto sotto, ma nessun controllo: si può salvare una partita IVA di tre cifre. `CampoForm` accetta già una prop `errore` collegata via `aria-describedby`, ma nessuna vista la usa.

**Perché conta.** Sono i campi che finiscono in fattura elettronica: l'errore si scopre allo scarto SDI, giorni dopo.

**Fix.** Validare al blur e passare il messaggio a `CampoForm`, che il collegamento accessibile lo fa già.

**Comando suggerito.** `impeccable harden`

### [P3] Residui di gergo e di struttura sulle schede

**Cosa.** "IN ARRIVO (V2)" espone un numero di versione interno e occupa stabilmente la colonna destra di ogni scheda anagrafica con sei voci non azionabili. In dashboard i KPI sono card dentro una card. Le liste corte lasciano centinaia di pixel vuoti.

**Fix.** Roadmap fuori dalla scheda, KPI come griglia su fondo pieno invece che tessere annidate, altezza minima del pannello legata al contenuto.

**Comando suggerito.** `impeccable distill`

## Persona Red Flags

**Alex (power user).** Ora può aprire un documento da tastiera, ma è tutto: non ordina per data né per importo, non seleziona più bolle, non ha una scorciatoia per la ricerca. Su un elenco di duemila anagrafiche non ha paginazione. Il guadagno rispetto alla prima passata è reale ma parziale: prima non poteva lavorare da tastiera, ora può solo navigare.

**Sam (screen reader, solo tastiera).** Il percorso è pulito: titolo e `h1` diversi per ogni rotta, tabelle con `scope` e `caption`, righe come link con nome parlante, 55 campi con label collegata e formato annunciato, zero controlli senza nome su cinque viste, contrasto sopra soglia ovunque. Restano: nessuno skip link (deve attraversare header e sidebar a ogni pagina), nessun `aria-live` sull'avanzamento del report, e il messaggio di blocco demo che arriva tre volte.

**Jordan (primo accesso).** Non incontra più mockup, Celery o UUID. Vede aree di lavoro leggibili al posto dei codici permesso e il formato atteso sotto i campi fiscali. Resta senza aiuto: "Nessuna notifica" non spiega cosa arriverà lì, la riga di assistenza nel login è ancora colorata come un link senza esserlo, e nessun campo diverso da quelli fiscali ha una spiegazione.

## Minor Observations

- Corretto in questa sessione: `backend/app/main.py:79` ora restituisce "Modalità demo" con l'accento; verificato sull'API locale.
- Il pannello notifiche resta aperto attraversando un cambio di route.
- Nessuno skip link.
- "SEDE LEGALE" e "SPEDIZIONE" sono etichette tracciate di secondo livello dentro un pannello che ne ha già una: la regola "una per pannello" è rispettata solo al primo livello.
- Sei scale di raggio ancora in uso, di cui due arbitrarie.
- Circa cinquanta usi del `red-*` di Tailwind per errori e azioni distruttive, invece dei token `brand-*`.
- Il tag "Usa PEC" ora è neutro ma sembra ancora un pulsante.
- Il bundle JS supera i 500 kB: nessun code splitting per rotta.
- L'unico gradiente rimasto è il pannello scuro del login (steel-900 → brand-900): tenuto di proposito come unico momento di identità, ora che ogni altra decorazione rossa è sparita.

## Questions to Consider

- Quante anagrafiche avrà un cliente reale al primo import? Se sono migliaia, la paginazione non è un P1 fra tanti: è la cosa che decide se l'app è usabile.
- Se l'operatore potesse premere un solo tasto per aprire la ricerca, quale sarebbe il tasto e da quale schermata?
- La demo in sola lettura sta insegnando agli utenti che il pulsante Salva non fa niente. Vale la pena disattivarlo davvero, invece di lasciarlo premere e poi negare?
