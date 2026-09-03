"""
M3 - Grafici
Scenario: Facility Management B2B fittizio (Project 01)

Legge il report KPI gia' calcolato in M2 e produce una versione finale
con due grafici a colonne incorporati nel file Excel:

1. Guasti totali per edificio, confronto 2024-2025-2026
2. ODL generati da impianti recidivi vs non recidivi, per anno
   (il grafico che sostiene visivamente il KPI piu' importante)
"""

import pandas as pd

FILE_INPUT = "kpi_report.xlsx"
FILE_OUTPUT = "kpi_report_con_grafici.xlsx"

ANNI_INTERESSE = [2024, 2025, 2026]


def prepara_tabella_recidivita(df_riepilogo: pd.DataFrame) -> pd.DataFrame:
    """
    Trasforma il riepilogo recidivita' in una tabella pronta per il grafico:
    Anno | ODL_da_recidivi | ODL_da_non_recidivi
    """
    df = df_riepilogo.copy()
    df["ODL_da_non_recidivi"] = df["ODL_totali_anno"] - df["ODL_generati_da_recidivi"]
    return df[["Anno", "ODL_generati_da_recidivi", "ODL_da_non_recidivi"]].rename(
        columns={"ODL_generati_da_recidivi": "ODL_da_impianti_recidivi"}
    )


def aggiungi_grafico_guasti_edificio(workbook, worksheet, sheet_name: str, n_rows: int, anchor_cell: str):
    chart = workbook.add_chart({"type": "column"})

    for i, anno in enumerate(ANNI_INTERESSE, start=1):
        chart.add_series({
            "name": f"{anno}",
            "categories": [sheet_name, 1, 0, n_rows, 0],  # colonna EDIFICIO
            "values": [sheet_name, 1, i, n_rows, i],
        })

    chart.set_title({"name": "Guasti totali per edificio (confronto 2024-2025-2026)"})
    chart.set_x_axis({"name": "Edificio"})
    chart.set_y_axis({"name": "Numero guasti"})
    chart.set_legend({"position": "bottom"})
    chart.set_size({"width": 720, "height": 380})

    worksheet.insert_chart(anchor_cell, chart)


def aggiungi_grafico_recidivita(workbook, worksheet, sheet_name: str, n_rows: int, anchor_cell: str):
    chart = workbook.add_chart({"type": "column", "subtype": "percent_stacked"})

    chart.add_series({
        "name": "ODL da impianti recidivi",
        "categories": [sheet_name, 1, 0, n_rows, 0],  # colonna Anno
        "values": [sheet_name, 1, 1, n_rows, 1],
    })
    chart.add_series({
        "name": "ODL da impianti non recidivi",
        "categories": [sheet_name, 1, 0, n_rows, 0],
        "values": [sheet_name, 1, 2, n_rows, 2],
    })

    chart.set_title({"name": "Quota ODL generata da impianti recidivi vs non recidivi"})
    chart.set_x_axis({"name": "Anno"})
    chart.set_y_axis({"name": "% del totale ODL"})
    chart.set_legend({"position": "bottom"})
    chart.set_size({"width": 720, "height": 380})

    worksheet.insert_chart(anchor_cell, chart)


if __name__ == "__main__":
    # Ricarica tutti i fogli gia' calcolati in M2, per ricostruire il file con i grafici
    fogli = pd.read_excel(FILE_INPUT, sheet_name=None)

    tab_guasti = fogli["KPI1_Guasti_Totali"]
    tab_riepilogo_recidivita = fogli["KPI3_Riepilogo_Recidivita"]
    tab_grafico_recidivita = prepara_tabella_recidivita(tab_riepilogo_recidivita)

    with pd.ExcelWriter(FILE_OUTPUT, engine="xlsxwriter") as writer:
        # Riscrive tutti i fogli originali, invariati
        for nome_foglio, df in fogli.items():
            df.to_excel(writer, sheet_name=nome_foglio, index=False)

        # Foglio dedicato al grafico 2 (dati preparati appositamente)
        tab_grafico_recidivita.to_excel(writer, sheet_name="Dati_Grafico_Recidivita", index=False)

        workbook = writer.book

        ws_guasti = writer.sheets["KPI1_Guasti_Totali"]
        aggiungi_grafico_guasti_edificio(
            workbook, ws_guasti, "KPI1_Guasti_Totali", len(tab_guasti), "H2"
        )

        ws_recidivita = writer.sheets["Dati_Grafico_Recidivita"]
        aggiungi_grafico_recidivita(
            workbook, ws_recidivita, "Dati_Grafico_Recidivita", len(tab_grafico_recidivita), "F2"
        )

    print(f"Report con grafici salvato: {FILE_OUTPUT}")
    print("Grafico 1: foglio 'KPI1_Guasti_Totali'")
    print("Grafico 2: foglio 'Dati_Grafico_Recidivita'")
