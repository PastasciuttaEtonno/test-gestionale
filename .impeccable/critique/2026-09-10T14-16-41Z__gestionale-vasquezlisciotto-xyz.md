---
target: gestionale.vasquezlisciotto.xyz (app live)
total_score: 20
p0_count: 0
p1_count: 3
timestamp: 2026-09-10T14-16-41Z
slug: gestionale-vasquezlisciotto-xyz
---
## Design Health Score

| # | Euristica | Voto | Problema chiave |
|---|-----------|------|-----------------|
| 1 | Visibilità dello stato | 3 | `<title>` e `<h1>` identici su tutte le route ("Gestionale Auth Client" / "Gestionale aziendale"); nessuna vista ha un titolo proprio |
| 2 | Corrispondenza col mondo reale | 2 | "ASYNC QUEUE DEMO", "Celery e SSE", "Redis Pub/Sub", UUID tenant in chiaro, `PERMESSI: ANAGRAFICHE.READ…`, `SRL / SPA / DITTA_INDIVIDUALE` |
| 3 | Controllo e libertà | 3 | Modale con Esc/Annulla/X e breadcrumb ok; nessun undo, banner demo non chiudibile, pannello notifiche non si chiude al cambio route |
| 4 | Coerenza e standard | 2 | Stesso stato documento con 3 codifiche colore diverse; 3 formati valuta; "Logout" vs "Esci"; modale vs rotta di dettaglio |
| 5 | Prevenzione degli errori | 2 | In demo il form è compilabile e "Salva modifiche" resta attivo; nessuna validazione inline su P.IVA/CF/SDI/PEC |
| 6 | Riconoscere invece che ricordare | 2 | Sei stati diversi resi con lo stesso pill rosa in dashboard; codici permesso grezzi; nessun titolo di pagina |
| 7 | Flessibilità ed efficienza | 1 | Zero scorciatoie da tastiera, nessun ordinamento colonne, nessuna paginazione, righe tabella solo mouse |
| 8 | Design estetico e minimale | 2 | La dashboard apre con una nota di lavorazione, poi 9 KPI, poi una demo infrastrutturale, prima dei documenti |
| 9 | Recupero dagli errori | 2 | Messaggio demo triplicato e con refuso; nessun errore a livello di campo |
| 10 | Aiuto e documentazione | 1 | L'intero sistema di aiuto è una riga non cliccabile nel login; empty state "Nessuna notifica" e basta |
| **Totale** | | **20/40** | **Acceptable (limite inferiore) — servono interventi significativi** |

## Anti-Patterns Verdict

**Valutazione LLM.** Non sembra generato da un'AI, e questo è un merito: la shell è coerente, la palette steel + rosso è una scelta e non un default, non ci sono viola SaaS né glassmorphism diffuso. Il problema è opposto: un unico gesto tipografico (maiuscoletto spaziato) è stato applicato 96 volte, e la dashboard espone all'utente finale la propria impalcatura tecnica.

**Scansione deterministica.** Il detector bundled non è presente in questa installazione (`scripts/detector/detect-antipatterns.mjs` assente): scansione CLI non disponibile. Sostituita con evidenza raccolta in browser e grep sui sorgenti:

- `tracking-widest|tracking-wider|tracking-[0.28em]`: **96 occorrenze** in 16 file. `AnagraficaDetailView.vue` da sola ne ha 23.
- Colori fuori sistema rispetto a DESIGN.md: `emerald-*`, `amber-*`, `blue-*`, `violet-*`, più il banner demo arancione. `violet-*` in `AnagraficheView.vue` e `AnagraficaDetailView.vue` è l'anti-reference "purple/indigo trustworthy accent" citata per nome in PRODUCT.md.
- Gradienti sul rosso brand, vietati esplicitamente da DESIGN.md §2: `AppShell.vue:31` `radial-gradient(circle at top, rgba(198,40,40,0.14), …)`, `DashboardView.vue:316` `linear-gradient(90deg,#8c1d18,#d2412e)`.
- Contrasto: label KPI e header tabella usano steel-400, misurati a **2.83:1** e **2.61:1** (soglia 4.5). PRODUCT.md vieta esplicitamente steel-400 come testo.
- 12 `<label>` nella modale anagrafica, **nessuna con `for`**, nessuna che avvolge l'input.
- 6 scale di raggio (`rounded-xl/2xl/lg/md/full` più `[1.5rem]` e `[2rem]`).
- Puliti: nessun gradient-text, nessun side-stripe border, un solo `backdrop-blur`. Le ombre passano da un unico token `--shadow-panel` invece che dalla scala preset di Tailwind.
- Console: pulita a parte "form field should have an id or name attribute" (×2).

**Overlay visivi.** Non disponibili: senza il detector bundled non è stato iniettato nulla nella pagina, quindi nel browser non è visibile nessun overlay.

## Overall Impression

La shell è buona. Sidebar scura ancorata, contenuto chiaro, responsive vero (sidebar che collassa, tabella che riduce le colonne), tabelle semantiche reali, dialog con `role="dialog"` e `aria-modal`, console pulita. Il livello artigianale è sopra la media dei gestionali web.

Quello che manca è la disciplina dentro quella shell. Il rosso brand doveva essere un segno di penna al massimo sul 10% dello schermo; oggi fa otto mestieri diversi (bottone primario, nav attiva, toggle, tag di stato, X di chiusura, errori, percentuale, marchio) e quindi non segnala più niente. Lo stato dei documenti, l'informazione più importante di un gestionale, è l'unica cosa che il colore non codifica in dashboard, e la codifica in modo diverso in `/bolle`. E la superficie principale mette una nota di lavorazione e una demo di Celery davanti all'elenco documenti.

L'occasione più grande: decidere cosa significa il colore, e far significare quello agli stati dei documenti.

## What's Working

1. **La vista di dettaglio anagrafica.** Breadcrumb, header identità con contatti cliccabili, gruppi logici (dati fiscali, SDI, indirizzi, note), riepilogo a destra. È l'unica schermata che si comporta come un documento invece che come una dashboard, ed è esattamente la direzione dichiarata in PRODUCT.md ("Document over dashboard").
2. **Il comportamento responsive.** A 390px la sidebar diventa hamburger, i KPI si impilano, la tabella riduce a Numero/Importo/Stato senza scroll orizzontale e senza overflow. Adattamento strutturale, non tipografia fluida: giusto per il register product.
3. **La scelta cromatica di base.** Steel neutri tinti di blu (`oklch(0.968 0.007 247.896)`) e un rosso saturo unico sono una posizione, non un default. E le ombre passano tutte da un unico token `--shadow-panel` invece che dalla scala preset: disciplina rara.

## Priority Issues

### [P1] Lo stato dei documenti non è leggibile né coerente

**Cosa.** In dashboard i sei stati (Da inviare, Aperta, Bozza, Confermata, Emessa, Da chiudere) rendono tutti con lo stesso pill: `background rgb(255,241,241)`, `color rgb(143,29,29)`, `border rgb(255,217,217)`. In `/bolle` gli stessi stati diventano teal (Emessa) e ambra (Bozza).

**Perché conta.** Lo stato è il campo che l'operatore scansiona per primo. In dashboard deve leggere sei etichette identiche una per una; passando a Bolle deve reimparare la codifica. È anche il caso "significato veicolato dal solo colore", che rompe la lettura per chi non distingue i rossi.

**Fix.** Una sola scala di stato in un token condiviso, applicata ovunque: neutro per bozza, ambra per in lavorazione, verde per emesso/confermato, rosso solo per ciò che richiede azione (Da inviare, Da chiudere). Affiancare sempre una forma o un'icona, non solo il colore.

**Comando suggerito.** `impeccable colorize`

### [P1] I campi del form principale non hanno label programmatiche

**Cosa.** Nella modale "Modifica anagrafica" ci sono 12 `<label>`, nessuna con `for` e nessuna che avvolge l'input. Il click sulla label non porta il fuoco nel campo; uno screen reader annuncia il placeholder o niente. Le ricerche nelle liste sono placeholder-as-label.

**Perché conta.** PRODUCT.md fissa come pavimento "form inputs paired with persistent labels", e Partita IVA, Codice Fiscale, SDI e PEC sono i campi su cui si sbaglia più spesso. È anche l'unica issue che Chrome segnala in console.

**Fix.** `for`/`id` su ogni coppia label-campo (o `<label>` che avvolge il controllo), `aria-describedby` per il formato atteso, label reale sopra i campi di ricerca.

**Comando suggerito.** `impeccable harden`

### [P1] Le tabelle sono raggiungibili solo col mouse

**Cosa.** Le righe sono `<tr class="cursor-pointer">` senza `tabindex`, senza `role` e senza handler da tastiera. In `/bolle` non esiste nessun altro modo di aprire un documento: zero elementi focusabili per riga. Nessun ordinamento colonne, nessuna paginazione, nessuna selezione multipla, nessuna scorciatoia in tutta l'app (17 elementi focusabili sull'intera dashboard).

**Perché conta.** PRODUCT.md descrive utenti che arrivano da un gestionale desktop VB6 e "expect dense forms, predictable layouts, keyboard flow". Oggi il flusso da tastiera non esiste. Chi lavora otto ore su questa schermata perde tempo a ogni riga.

**Fix.** Riga come `<a>` oppure `<tr tabindex="0">` con Enter/Spazio, focus ring visibile, header ordinabili con `aria-sort`, `/` per la ricerca, `n` per il nuovo documento.

**Comando suggerito.** `impeccable harden`

### [P2] La dashboard mette la propria impalcatura davanti al lavoro

**Cosa.** Prima dell'elenco documenti l'utente incontra: "Mockup statico di una home ERP enterprise con sidebar, toolbar e griglia dati densa. Serve solo a validare ingombri, gerarchia visiva e leggibilità", 4 KPI tile, altri 5 KPI tile, e un pannello "ASYNC QUEUE DEMO / Generazione report con Celery e SSE" che spiega Redis Pub/Sub e Server-Sent Events, con l'UUID del tenant in un campo di testo e la lista `PERMESSI: ANAGRAFICHE.READ, ANAGRAFICHE.WRITE, …`.

**Perché conta.** PRODUCT.md dichiara "hero-metric tiles" come anti-reference e "Document over dashboard" come primo principio. Su mobile sono circa 1500px di scroll prima del primo documento. La nota di mockup è una nota di lavorazione rimasta in produzione.

**Fix.** Rimuovere la nota di mockup; ridurre i KPI a 3 che portano da qualche parte; spostare il pannello Celery in una pagina "Diagnostica" riservata; sostituire l'UUID con un selettore di tenant per nome e i codici permesso con etichette leggibili.

**Comando suggerito.** `impeccable distill`

### [P2] Il maiuscoletto spaziato è l'unico gesto tipografico dell'app

**Cosa.** 96 occorrenze di `tracking-widest`/`tracking-wider`/`tracking-[0.28em]` in 16 file. Etichette di sezione, header tabella, badge ruolo, nomi campo del form ("TIPO *", "RAGIONE SOCIALE *", "PARTITA IVA"): tutto maiuscolo a 12px con 1.2px di spaziatura. `AnagraficaDetailView.vue` ne ha 23 in una schermata.

**Perché conta.** Il maiuscoletto spaziato disattiva il riconoscimento della forma della parola: si legge lettera per lettera. Applicato ai nomi dei campi in un form di data entry usato tutto il giorno è una tassa su ogni saccade. È anche il "tracked eyebrow" che la skill frontend-design cita come segnale di lavoro generico.

**Fix.** Tenerlo per le etichette di sezione di primo livello, una per pannello al massimo. Nomi campo e header tabella in sentence case, peso 500-600, spaziatura normale, un gradino di scala sotto il valore.

**Comando suggerito.** `impeccable typeset`

### [P2] Contrasto sotto soglia sulle etichette dati

**Cosa.** `steel-400` (`#8b95a1`) usato per le label KPI (**2.83:1**), gli header tabella della dashboard (**2.61:1**) e il timestamp "Aggiornato 16:07:45" (**3.04:1**). Su `/bolle` gli header sono a **4.41:1**, appena sotto la soglia di 4.5.

**Perché conta.** PRODUCT.md scrive testualmente "avoid steel-400 on white for body text". La regola esiste già, il codice non la rispetta. E sono proprio le etichette che dicono cosa sia il numero accanto.

**Fix.** Portare label e header a `steel-700` (`#39424d`). Riservare `steel-400` a placeholder e stati disabilitati.

**Comando suggerito.** `impeccable polish`

## Persona Red Flags

**Alex (power user).** Nessuna scorciatoia da tastiera in tutta l'app. Non può ordinare per data o importo. Non può selezionare più bolle. Per aprire una bolla deve usare il mouse: la riga non è focusabile. Su `/anagrafiche` il pulsante di modifica apre una modale anche se esiste la rotta `/anagrafiche/:id`: due percorsi per la stessa cosa, nessuno dei due invocabile da tastiera. Alex torna al gestionale vecchio entro la prima settimana.

**Sam (screen reader, solo tastiera).** Tre pulsanti senza nome accessibile nell'header (toggle sidebar, campanella notifiche, collapse). `<title>` e `<h1>` identici su ogni route: navigando non sa dove è arrivato, e su `/bolle` la pagina non ha nessun heading oltre all'h1 globale. `<th>` senza `scope`, tabella senza `caption`. Le 12 label del form non sono associate ai campi. Gli stati documento in dashboard sono distinguibili solo dal testo perché il colore è identico, il che ironicamente lo aiuta più degli altri. Nessuno skip link. Una sola regola `:focus-visible` in tutto il CSS compilato.

**Jordan (primo accesso).** Legge in dashboard che sta guardando un "mockup statico… serve solo a validare ingombri" e non sa se il sistema è reale. Poi trova "Generazione report con Celery e SSE" e un UUID. Cerca aiuto: l'unica riga è "Per assistenza contattare il proprio amministratore di sistema", nel login, colorata come un link ma non cliccabile. Apre le notifiche: "Nessuna notifica", senza nessuna spiegazione di cosa arriverà lì. Compila la modale, preme Salva e riceve lo stesso messaggio tre volte insieme (banner in alto, riquadro nel form, toast in basso), scritto "Modalita" senza accento.

## Minor Observations

- `backend/app/main.py:79` restituisce `"Modalita demo: le modifiche non vengono salvate."` senza accento e `frontend/src/lib/http.js:57` la stampa verbatim, mentre `App.vue:69` e `useDemo.js:16` scrivono correttamente "Modalità". Refuso di un carattere, visibile due volte a ogni tentativo di salvataggio.
- Tre formati di valuta: `12.480,00 EUR` (dashboard), `14,20 €` (articoli), `1301,74 €` (bolle, senza separatore delle migliaia).
- "Logout" a desktop diventa "Esci" a 390px: stessa azione, due parole.
- Valore vuoto reso `-` in dashboard e `— bozza` in `/bolle` (monospazio, minuscolo).
- Il pannello notifiche resta aperto attraversando un cambio di route.
- `AnagraficaDetailView`: il pannello "INDIRIZZI (2)" contiene due card annidate, card dentro card.
- "IN ARRIVO (V2)" occupa stabilmente la colonna destra di ogni scheda anagrafica con sei voci non azionabili, ed espone all'utente un numero di versione interno.
- Colonna "AZIONI" presente su `/anagrafiche` e `/articoli`, assente su `/bolle`.
- Il tag "Usa PEC" accanto al Codice SDI sembra un pulsante ma non lo è.
- `NATURA GIURIDICA` ha placeholder `SRL / SPA / DITTA_INDIVIDUALE`: un enum di codice, con underscore, mostrato in UI.
- Il pulsante "Salva modifiche" resta primario e attivo anche in modalità demo di sola lettura.
- `*` per i campi obbligatori senza legenda.
- Nessuna `<meta name="description">`; `<title>` è "Gestionale Auth Client", un nome da repository.
- La login mostra un pannello marketing con bullet ("Gestione ordini, bolle e fatture") in un'app a cui si accede solo con credenziali aziendali già assegnate.
- Su `/bolle` due righe di dati sono seguite da circa 500px di pagina vuota: il layout non ha uno stato per liste corte.
- A 390px la stringa "PERMESSI: …" trabocca visivamente dal proprio contenitore arrotondato.
- 6 scale di raggio in uso, di cui due arbitrarie (`rounded-[1.5rem]`, `rounded-[2rem]`).

## Questions to Consider

- Se il colore dovesse dire una sola cosa in tutta l'app, cosa sceglieresti: "questo è lo stato del documento" o "questo è il pulsante primario"? Oggi prova a dire entrambe e non dice nessuna delle due.
- La dashboard serve davvero a chi deve lavorare, o è una vetrina per chi valuta il prodotto? Se è la seconda, dovrebbe essere una pagina a parte e non la landing dopo il login.
- Cosa succederebbe alla percezione dell'app se la vista di dettaglio anagrafica diventasse il modello per tutte le altre, invece della dashboard?
