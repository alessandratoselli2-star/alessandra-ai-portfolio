"""
M5 - Executive Summary AI
Scenario: Facility Management B2B fittizio (Project 01)

NOTA METODOLOGICA IMPORTANTE:
Questo script mostra la STRUTTURA che avrebbe una chiamata reale
all'API di Claude per generare l'executive summary a partire dai KPI.
La chiamata API vera e' commentata: per farla funzionare serve una
chiave API valida (ANTHROPIC_API_KEY) e la libreria 'anthropic'.

In questa fase di apprendimento, il testo dell'executive summary e'
gia' fornito come esempio (generato manualmente con la stessa logica
che seguirebbe una chiamata API reale), cosi' puoi vedere subito il
risultato finale senza dover configurare credenziali.
"""

import json

# ==========================
# DATI DI INPUT (dai KPI gia' calcolati in M2/M4)
# ==========================

KPI_2025 = {
    "anno": 2025,
    "impianti_con_guasto_totali": 1028,
    "impianti_recidivi": 295,
    "perc_impianti_recidivi": 28.7,
    "odl_totali_anno": 1526,
    "odl_generati_da_recidivi": 793,
    "perc_odl_da_recidivi": 52.0,
}


def costruisci_prompt(kpi: dict) -> str:
    """Costruisce il prompt che verrebbe inviato all'API, a partire dai numeri KPI."""
    return f"""Sei un analista che scrive un breve executive summary per un board aziendale
di una societa' di Facility Management. Usa linguaggio manageriale, diretto,
senza gergo tecnico. Massimo 120 parole. Parti dal numero piu' rilevante.

Dati anno {kpi['anno']}:
- Impianti con almeno un guasto: {kpi['impianti_con_guasto_totali']}
- Di cui con guasti ripetuti (recidivi): {kpi['impianti_recidivi']} ({kpi['perc_impianti_recidivi']}%)
- ODL totali nell'anno: {kpi['odl_totali_anno']}
- ODL generati dagli impianti recidivi: {kpi['odl_generati_da_recidivi']} ({kpi['perc_odl_da_recidivi']}%)

Scrivi un breve paragrafo che comunichi il pattern principale e l'implicazione
operativa, in modo che chi legge capisca subito dove concentrare l'attenzione."""


def chiamata_api_reale(prompt: str) -> str:
    """
    Questa e' la funzione che, con una chiave API valida, farebbe la chiamata vera.
    Lasciata commentata: decommentare e configurare ANTHROPIC_API_KEY per attivarla.
    """
    # import anthropic
    # client = anthropic.Anthropic(api_key="LA_TUA_CHIAVE_API")
    # response = client.messages.create(
    #     model="claude-sonnet-4-6",
    #     max_tokens=300,
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return response.content[0].text
    raise NotImplementedError("Chiamata API non attiva in questo esercizio didattico.")


# ==========================
# TESTO DI ESEMPIO (equivalente al risultato che darebbe la chiamata API)
# ==========================

EXECUTIVE_SUMMARY_ESEMPIO = """Nel 2025, il 28,7% degli impianti con guasto (295 su 1.028) ha registrato \
interventi ripetuti nello stesso anno. Questo sottoinsieme, pur essendo meno di un terzo del totale, \
ha generato il 52% di tutti gli ordini di lavoro dell'anno (793 su 1.526).

Il pattern e' chiaro: il carico di lavoro tecnico non e' distribuito uniformemente sul parco impianti, \
ma si concentra su un gruppo relativamente contenuto di asset problematici. Un intervento mirato di \
manutenzione straordinaria o sostituzione su questi impianti recidivi avrebbe un impatto \
sproporzionatamente alto sulla riduzione del carico complessivo, rispetto a un intervento uniforme \
su tutto il parco."""


if __name__ == "__main__":
    prompt = costruisci_prompt(KPI_2025)

    print(">>> PROMPT CHE VERREBBE INVIATO ALL'API\n")
    print(prompt)

    print("\n>>> EXECUTIVE SUMMARY (esempio, stessa logica di una risposta AI reale)\n")
    print(EXECUTIVE_SUMMARY_ESEMPIO)

    # Salva entrambi su file, utili per M6 (slide) e per la documentazione
    with open("executive_summary.txt", "w", encoding="utf-8") as f:
        f.write(EXECUTIVE_SUMMARY_ESEMPIO)

    with open("prompt_usato.txt", "w", encoding="utf-8") as f:
        f.write(prompt)

    print("\nFile salvati: executive_summary.txt, prompt_usato.txt")
