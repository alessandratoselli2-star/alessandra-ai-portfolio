"""
M1 - Data Quality
Scenario: Facility Management B2B fittizio (Project 01)

Pulisce il dataset sintetico generato in M0, gestendo:
- formati data misti
- incoerenze testuali (spazi, maiuscole)
- codici IMPIANTO placeholder
- valori mancanti su colonne secondarie
- duplicati esatti

Principio guida: ogni correzione/scarto viene REGISTRATO in un log,
mai fatto "in silenzio". Il log finale e' parte dell'output, non un
dettaglio tecnico nascosto.
"""

import pandas as pd
from datetime import datetime

FILE_INPUT = "dataset_sintetico_fm.xlsx"
FILE_OUTPUT = "dataset_pulito_fm.xlsx"

SHEET_ODL = "ODL"
SHEET_ANAGRAFICA = "Anagrafica_Impianti"

PLACEHOLDER_IMPIANTO = {"-", "NA", "", "N/A"}

# Formati data attesi, in ordine di tentativo
FORMATI_DATA = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%y", "%d.%m.%Y"]


def parse_data_robusta(valore):
    """
    Prova piu' formati in sequenza. Restituisce (data_parsata, esito)
    dove esito e' una stringa che spiega il risultato, utile per il log.
    """
    if pd.isna(valore) or str(valore).strip() == "":
        return None, "mancante"

    testo = str(valore).strip()

    for fmt in FORMATI_DATA:
        try:
            dt = datetime.strptime(testo, fmt)
            # controllo di sanita': scartiamo date fuori da un range plausibile
            if dt.year < 2020 or dt.year > 2030:
                return None, "anno implausibile"
            return dt, "ok"
        except ValueError:
            continue

    return None, "formato non riconosciuto o data inesistente"


def pulisci_dataset(file_input: str):
    df_odl = pd.read_excel(file_input, sheet_name=SHEET_ODL)
    df_anagrafica = pd.read_excel(file_input, sheet_name=SHEET_ANAGRAFICA)

    n_righe_iniziali = len(df_odl)
    log_eventi = []  # lista di dict, diventera' il foglio "Log_Qualita"

    # --- 1) Normalizzazione testi ---
    df_odl["EDIFICIO"] = df_odl["EDIFICIO"].astype("string").str.strip().str.upper()
    df_odl["IMPIANTO"] = df_odl["IMPIANTO"].astype("string").str.strip()

    # --- 2) Parsing date robusto ---
    risultati = df_odl["DATA_CREAZIONE"].apply(parse_data_robusta)
    df_odl["DATA_CREAZIONE_PARSED"] = [r[0] for r in risultati]
    df_odl["_esito_data"] = [r[1] for r in risultati]

    conteggio_esiti = df_odl["_esito_data"].value_counts()
    for esito, conteggio in conteggio_esiti.items():
        if esito != "ok":
            log_eventi.append({
                "Fase": "Parsing data",
                "Problema": esito,
                "Righe_coinvolte": int(conteggio),
                "Azione": "Riga scartata"
            })

    righe_data_invalida = (df_odl["_esito_data"] != "ok").sum()
    df_odl = df_odl[df_odl["_esito_data"] == "ok"].copy()
    df_odl["DATA_CREAZIONE"] = df_odl["DATA_CREAZIONE_PARSED"]
    df_odl = df_odl.drop(columns=["DATA_CREAZIONE_PARSED", "_esito_data"])

    # --- 3) Codici IMPIANTO placeholder ---
    maschera_placeholder = df_odl["IMPIANTO"].isin(PLACEHOLDER_IMPIANTO) | df_odl["IMPIANTO"].isna()
    n_placeholder = int(maschera_placeholder.sum())
    if n_placeholder > 0:
        log_eventi.append({
            "Fase": "Codice impianto",
            "Problema": "Placeholder o mancante (- / NA / vuoto)",
            "Righe_coinvolte": n_placeholder,
            "Azione": "Escluse dai calcoli KPI (mantenute in foglio a parte)"
        })

    df_impianto_invalido = df_odl[maschera_placeholder].copy()
    df_odl = df_odl[~maschera_placeholder].copy()

    # --- 4) Valori mancanti su colonne secondarie: non scartiamo, segnaliamo ---
    for col in ["TECNICO", "FORNITORE", "STATUS"]:
        n_mancanti = int(df_odl[col].isna().sum())
        if n_mancanti > 0:
            log_eventi.append({
                "Fase": "Valori mancanti",
                "Problema": f"{col} mancante",
                "Righe_coinvolte": n_mancanti,
                "Azione": "Impostato a 'Non specificato' (riga mantenuta)"
            })
        df_odl[col] = df_odl[col].fillna("Non specificato")

    # --- 5) Duplicati esatti ---
    n_duplicati = int(df_odl.duplicated().sum())
    if n_duplicati > 0:
        log_eventi.append({
            "Fase": "Duplicati",
            "Problema": "Righe identiche in tutte le colonne",
            "Righe_coinvolte": n_duplicati,
            "Azione": "Rimosse, mantenuta una sola copia"
        })
    df_odl = df_odl.drop_duplicates().copy()

    # --- Riepilogo finale ---
    n_righe_finali = len(df_odl)
    log_eventi.append({
        "Fase": "RIEPILOGO",
        "Problema": "Righe iniziali vs finali",
        "Righe_coinvolte": n_righe_iniziali - n_righe_finali,
        "Azione": f"{n_righe_iniziali} righe iniziali -> {n_righe_finali} righe pulite e valide "
                  f"({n_placeholder} escluse per impianto invalido, restano nel foglio dedicato)"
    })

    df_log = pd.DataFrame(log_eventi)

    return df_odl, df_impianto_invalido, df_anagrafica, df_log


if __name__ == "__main__":
    df_pulito, df_impianto_invalido, df_anagrafica, df_log = pulisci_dataset(FILE_INPUT)

    print(">>> RIEPILOGO QUALITA' DATI")
    print(df_log.to_string(index=False))

    with pd.ExcelWriter(FILE_OUTPUT, engine="xlsxwriter") as writer:
        df_pulito.to_excel(writer, sheet_name="ODL_Pulito", index=False)
        df_impianto_invalido.to_excel(writer, sheet_name="Righe_Impianto_Invalido", index=False)
        df_anagrafica.to_excel(writer, sheet_name="Anagrafica_Impianti", index=False)
        df_log.to_excel(writer, sheet_name="Log_Qualita", index=False)

    print(f"\nFile pulito salvato: {FILE_OUTPUT}")
