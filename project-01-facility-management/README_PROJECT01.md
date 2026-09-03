# Project 01 — Automated Operations Performance Reporting

Pipeline end-to-end per il reporting mensile di performance operativa su un parco impianti, con KPI di recidività dei guasti calcolati sia via Python che via formule Excel live, executive summary generato con AI, slide per il management, e automazione dell'esecuzione mensile.

> **Nota sui dati**: dataset interamente sintetico (scenario B2B Facility Management fittizio, Italia). Nessun dato aziendale reale è contenuto in questo repository.

## Il problema che affronta

Su un parco di impianti distribuiti su più edifici, i guasti non sono distribuiti uniformemente: un sottoinsieme relativamente piccolo di impianti genera una quota sproporzionata degli interventi. Questa pipeline identifica quel sottoinsieme ("impianti recidivi") e lo comunica in modo chiaro a chi deve decidere dove allocare risorse di manutenzione.

**Risultato chiave (anno 2025, dati sintetici)**: il 28,7% degli impianti con guasto ha avuto interventi ripetuti, generando il 52% di tutti gli ordini di lavoro dell'anno.

## Struttura della pipeline (M0 → M7)

| Fase | Cosa fa | Script |
|---|---|---|
| M0 | Genera il dataset sintetico ODL, con imperfezioni intenzionali (date miste, duplicati, valori mancanti) | `scripts/genera_dataset_sintetico.py` |
| M1 | Pulizia dati, con log di trasparenza su ogni scarto/correzione | `scripts/pulisci_dati.py` |
| M2 | Calcolo KPI (guasti totali, % impianti con guasto, recidività) | `scripts/kpi_engine.py` |
| M3 | Grafici a supporto dei KPI | `scripts/grafici.py` |
| M4 | Report Excel a **formule live** (non valori precalcolati) | `scripts/report_live.py` |
| M5 | Executive summary in linguaggio manageriale (struttura prompt AI) | `scripts/executive_summary.py` |
| M6 | Slide management (Executive Deck a 5 slide, Canva) | — |
| M7 | Orchestrazione mensile automatica (Claude Cowork, scheduled task) | — |

## Come eseguirla

```bash
python3 scripts/genera_dataset_sintetico.py
python3 scripts/pulisci_dati.py
python3 scripts/kpi_engine.py
python3 scripts/grafici.py
python3 scripts/report_live.py
python3 scripts/executive_summary.py
```

Oppure, se hai la skill Claude installata: basta chiedere *"genera il report Facility Management"*.

## Una lezione di metodo, non solo di codice

Durante lo sviluppo, un confronto incrociato tra il calcolo dei KPI in Python (M2) e le formule Excel live (M4) ha rivelato una discrepanza nei numeri di recidività. La causa: una collisione nei codici identificativi degli impianti tra due edifici con lo stesso prefisso, che mascherava un bug nel conteggio degli impianti distinti. Bug corretto e risultato riverificato fino a coincidenza esatta tra le due implementazioni indipendenti.

Questo è il motivo per cui il report finale (M4) usa formule Excel live invece di valori precalcolati: chiunque riceva il file può verificare ogni numero aprendo la cella, senza doversi fidare di uno script invisibile.

## Struttura del repository

```
data/       - dataset grezzo, pulito, e report intermedi
scripts/    - pipeline Python, eseguibile in sequenza
output/     - report finali e file pronti per la presentazione
```

## Slide di sintesi

Executive Deck a 5 slide (Canva): [link al design](https://www.canva.com/d/ZtUpARXi_BUWE6s)
