"""
M2 - KPI Engine
Scenario: Facility Management B2B fittizio (Project 01)

KPI calcolati, a partire dal dataset pulito in M1:
1. Guasti totali per edificio/anno
2. % impianti con almeno un guasto sul totale impianti (da Anagrafica_Impianti)
3. Recidivita' del guasto: impianti con >= SOGLIA_RECIDIVITA interventi nello stesso periodo

Il motore e' parametrico: cambiando ANNI_INTERESSE o SOGLIA_RECIDIVITA
non serve toccare la logica sottostante.
"""

import pandas as pd

FILE_INPUT = "dataset_pulito_fm.xlsx"
FILE_OUTPUT = "kpi_report.xlsx"

SHEET_ODL = "ODL_Pulito"
SHEET_ANAGRAFICA = "Anagrafica_Impianti"

ANNI_INTERESSE = [2024, 2025, 2026]
SOGLIA_RECIDIVITA = 2  # numero minimo di interventi per considerare un impianto "recidivo"


def carica_dati(file_input: str):
    df_odl = pd.read_excel(file_input, sheet_name=SHEET_ODL)
    df_anagrafica = pd.read_excel(file_input, sheet_name=SHEET_ANAGRAFICA)

    df_odl["DATA_CREAZIONE"] = pd.to_datetime(df_odl["DATA_CREAZIONE"])
    df_odl["Anno"] = df_odl["DATA_CREAZIONE"].dt.year
    df_odl["Mese"] = df_odl["DATA_CREAZIONE"].dt.month

    return df_odl, df_anagrafica


def kpi_guasti_totali(df_odl: pd.DataFrame, anni: list) -> pd.DataFrame:
    """KPI 1: numero di ODL (guasti) per edificio, per ciascun anno di interesse."""
    df = df_odl[df_odl["Anno"].isin(anni)]
    tab = (
        df.groupby(["EDIFICIO", "Anno"])
        .size()
        .reset_index(name="N_Guasti")
        .pivot(index="EDIFICIO", columns="Anno", values="N_Guasti")
        .fillna(0)
        .astype(int)
        .reset_index()
    )
    tab.columns = ["EDIFICIO"] + [f"Guasti_{a}" for a in tab.columns[1:]]
    return tab


def kpi_perc_impianti_con_guasto(df_odl: pd.DataFrame, df_anagrafica: pd.DataFrame, anno: int) -> pd.DataFrame:
    """KPI 2: quota di impianti con almeno un guasto nell'anno, rispetto al totale impianti dell'edificio."""
    df_anno = df_odl[df_odl["Anno"] == anno]

    impianti_con_guasto = (
        df_anno.groupby("EDIFICIO")["IMPIANTO"]
        .nunique()
        .reset_index(name=f"Impianti_con_guasto_{anno}")
    )

    tab = df_anagrafica.merge(impianti_con_guasto, on="EDIFICIO", how="left")
    col_guasto = f"Impianti_con_guasto_{anno}"
    tab[col_guasto] = tab[col_guasto].fillna(0).astype(int)

    col_perc = f"Perc_impianti_con_guasto_{anno}"
    tab[col_perc] = (tab[col_guasto] / tab["N_IMPIANTI_TOTALI"] * 100).round(1)

    return tab


def kpi_recidivita(df_odl: pd.DataFrame, anno: int, soglia: int = SOGLIA_RECIDIVITA):
    """
    KPI 3: Recidivita' del guasto.
    Restituisce:
    - dettaglio: EDIFICIO | IMPIANTO | N_Interventi (solo impianti >= soglia)
    - riepilogo: statistiche aggregate per la headline del report
    """
    df_anno = df_odl[df_odl["Anno"] == anno]

    counts = (
        df_anno.groupby(["EDIFICIO", "IMPIANTO"])
        .size()
        .reset_index(name="N_Interventi")
    )

    dettaglio = (
        counts[counts["N_Interventi"] >= soglia]
        .sort_values("N_Interventi", ascending=False)
        .reset_index(drop=True)
    )

    n_impianti_totali_con_guasto = len(counts[["EDIFICIO", "IMPIANTO"]].drop_duplicates())
    n_impianti_recidivi = dettaglio["IMPIANTO"].nunique()
    odl_totali_anno = len(df_anno)
    odl_da_recidivi = dettaglio["N_Interventi"].sum()

    riepilogo = {
        "Anno": anno,
        "Soglia_recidivita": soglia,
        "Impianti_con_guasto_totali": n_impianti_totali_con_guasto,
        "Impianti_recidivi": n_impianti_recidivi,
        "Perc_impianti_recidivi": round(n_impianti_recidivi / n_impianti_totali_con_guasto * 100, 1)
            if n_impianti_totali_con_guasto else 0,
        "ODL_totali_anno": odl_totali_anno,
        "ODL_generati_da_recidivi": int(odl_da_recidivi),
        "Perc_ODL_da_recidivi": round(odl_da_recidivi / odl_totali_anno * 100, 1)
            if odl_totali_anno else 0,
    }

    return dettaglio, riepilogo


if __name__ == "__main__":
    df_odl, df_anagrafica = carica_dati(FILE_INPUT)

    print(">>> KPI 1 - Guasti totali per edificio/anno")
    tab_guasti = kpi_guasti_totali(df_odl, ANNI_INTERESSE)
    print(tab_guasti.to_string(index=False))

    print("\n>>> KPI 2 - % impianti con guasto (anno piu' recente completo: 2025)")
    tab_perc = kpi_perc_impianti_con_guasto(df_odl, df_anagrafica, 2025)
    print(tab_perc.to_string(index=False))

    print("\n>>> KPI 3 - Recidivita' del guasto, per anno")
    riepiloghi = []
    dettagli_per_anno = {}
    for anno in ANNI_INTERESSE:
        dettaglio, riepilogo = kpi_recidivita(df_odl, anno)
        dettagli_per_anno[anno] = dettaglio
        riepiloghi.append(riepilogo)
        print(f"\nAnno {anno}: {riepilogo}")

    df_riepilogo_recidivita = pd.DataFrame(riepiloghi)

    with pd.ExcelWriter(FILE_OUTPUT, engine="xlsxwriter") as writer:
        tab_guasti.to_excel(writer, sheet_name="KPI1_Guasti_Totali", index=False)
        tab_perc.to_excel(writer, sheet_name="KPI2_Perc_Impianti_Guasto", index=False)
        df_riepilogo_recidivita.to_excel(writer, sheet_name="KPI3_Riepilogo_Recidivita", index=False)
        for anno in ANNI_INTERESSE:
            dettagli_per_anno[anno].to_excel(writer, sheet_name=f"KPI3_Dettaglio_{anno}", index=False)

    print(f"\nReport KPI salvato: {FILE_OUTPUT}")
