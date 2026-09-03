"""
M4 - Report Excel a formule live
Scenario: Facility Management B2B fittizio (Project 01)

A differenza di M2 (dove i KPI erano calcolati in Python e scritti come
valori), qui i dati grezzi puliti vengono scritti in Excel e i KPI sono
formule live (COUNTIFS/SUMIFS) che chiunque puo' verificare aprendo il file.

La soglia di recidivita' e' in una cella parametro (foglio Parametri):
cambiandola li', tutto il report si ricalcola da solo.
"""

import pandas as pd

FILE_INPUT = "dataset_pulito_fm.xlsx"
FILE_OUTPUT = "report_live_fm.xlsx"

SHEET_ODL = "ODL_Pulito"
SHEET_ANAGRAFICA = "Anagrafica_Impianti"

ANNI_INTERESSE = [2024, 2025, 2026]
SOGLIA_RECIDIVITA_DEFAULT = 2


def main():
    df_odl = pd.read_excel(FILE_INPUT, sheet_name=SHEET_ODL)
    df_anagrafica = pd.read_excel(FILE_INPUT, sheet_name=SHEET_ANAGRAFICA)

    df_odl["DATA_CREAZIONE"] = pd.to_datetime(df_odl["DATA_CREAZIONE"])
    n = len(df_odl)  # numero di righe dati (senza header)
    prima_riga = 2   # in Excel, riga 1 = header, riga 2 = primo dato
    ultima_riga = n + 1

    edifici = sorted(df_odl["EDIFICIO"].unique().tolist())

    import xlsxwriter
    workbook = xlsxwriter.Workbook(FILE_OUTPUT)

    fmt_header = workbook.add_format({"bold": True, "bg_color": "#DDEBF7", "border": 1})
    fmt_perc = workbook.add_format({"num_format": "0.0"})
    fmt_data = workbook.add_format({"num_format": "dd/mm/yyyy"})

    # ==========================
    # FOGLIO PARAMETRI
    # ==========================
    ws_param = workbook.add_worksheet("Parametri")
    ws_param.write("A1", "Soglia recidivita' (n. minimo interventi)", fmt_header)
    ws_param.write("B1", SOGLIA_RECIDIVITA_DEFAULT)
    ws_param.write("A3", "Modifica il valore in B1 per ricalcolare automaticamente tutto il report.")
    ws_param.set_column("A:A", 45)

    # ==========================
    # FOGLIO BASE_ODL (dati + colonne di supporto a formula)
    # ==========================
    ws_base = workbook.add_worksheet("Base_ODL")
    colonne_base = [
        "ID_ODL", "EDIFICIO", "IMPIANTO", "TIPO_GUASTO", "DATA_CREAZIONE",
        "STATUS", "TECNICO", "FORNITORE", "Anno", "Mese",
        "N_Interventi_Impianto_Anno", "Primo_Occorrenza", "Recidivo_Flag", "Primo_E_Recidivo"
    ]
    for c, nome in enumerate(colonne_base):
        ws_base.write(0, c, nome, fmt_header)

    for i, row in df_odl.reset_index(drop=True).iterrows():
        r = i + 1  # riga excel (0-indexed per xlsxwriter, riga 1 = seconda riga foglio)
        ws_base.write(r, 0, row["ID_ODL"])
        ws_base.write(r, 1, row["EDIFICIO"])
        ws_base.write(r, 2, row["IMPIANTO"])
        ws_base.write(r, 3, row["TIPO_GUASTO"])
        ws_base.write_datetime(r, 4, row["DATA_CREAZIONE"], fmt_data)
        ws_base.write(r, 5, row["STATUS"])
        ws_base.write(r, 6, row["TECNICO"])
        ws_base.write(r, 7, row["FORNITORE"])

        riga_excel = r + 1  # numero di riga reale in Excel (1-indexed, header=1)

        # Anno / Mese come formule dalla data
        ws_base.write_formula(r, 8, f"=YEAR(E{riga_excel})")
        ws_base.write_formula(r, 9, f"=MONTH(E{riga_excel})")

        # N interventi dello stesso impianto (edificio+impianto+anno) sull'intero range
        ws_base.write_formula(
            r, 10,
            f"=COUNTIFS($B$2:$B${ultima_riga},B{riga_excel},"
            f"$C$2:$C${ultima_riga},C{riga_excel},"
            f"$I$2:$I${ultima_riga},I{riga_excel})"
        )

        # Prima occorrenza di quella combinazione edificio+impianto+anno (per contare impianti distinti)
        ws_base.write_formula(
            r, 11,
            f"=IF(COUNTIFS($B$2:B{riga_excel},B{riga_excel},"
            f"$C$2:C{riga_excel},C{riga_excel},"
            f"$I$2:I{riga_excel},I{riga_excel})=1,1,0)"
        )

        # Flag recidivo, soglia parametrica da foglio Parametri
        ws_base.write_formula(r, 12, f"=IF(K{riga_excel}>=Parametri!$B$1,1,0)")

        # Combinazione: e' la prima occorrenza ED e' recidivo (per contare impianti recidivi distinti)
        ws_base.write_formula(r, 13, f"=L{riga_excel}*M{riga_excel}")

    ws_base.set_column("A:A", 12)
    ws_base.set_column("B:B", 22)
    ws_base.set_column("E:E", 12)
    ws_base.autofilter(0, 0, n, len(colonne_base) - 1)

    # ==========================
    # FOGLIO ANAGRAFICA_IMPIANTI (invariato, copia diretta)
    # ==========================
    ws_anag = workbook.add_worksheet("Anagrafica_Impianti")
    ws_anag.write(0, 0, "EDIFICIO", fmt_header)
    ws_anag.write(0, 1, "N_IMPIANTI_TOTALI", fmt_header)
    for i, row in df_anagrafica.reset_index(drop=True).iterrows():
        ws_anag.write(i + 1, 0, row["EDIFICIO"])
        ws_anag.write(i + 1, 1, row["N_IMPIANTI_TOTALI"])
    ws_anag.set_column("A:A", 25)

    # ==========================
    # FOGLIO KPI1 - Guasti totali per edificio/anno (formule live)
    # ==========================
    ws_k1 = workbook.add_worksheet("KPI1_Guasti_Totali")
    intestazioni_k1 = ["EDIFICIO"] + [f"Guasti_{a}" for a in ANNI_INTERESSE]
    for c, nome in enumerate(intestazioni_k1):
        ws_k1.write(0, c, nome, fmt_header)

    for i, edificio in enumerate(edifici):
        r = i + 1
        ws_k1.write(r, 0, edificio)
        for j, anno in enumerate(ANNI_INTERESSE):
            ws_k1.write_formula(
                r, j + 1,
                f'=COUNTIFS(Base_ODL!$B$2:$B${ultima_riga},A{r+1},'
                f'Base_ODL!$I$2:$I${ultima_riga},{anno})'
            )
    ws_k1.set_column("A:A", 25)

    # ==========================
    # FOGLIO KPI2 - % impianti con guasto (anno piu' recente completo: 2025)
    # ==========================
    ws_k2 = workbook.add_worksheet("KPI2_Perc_Impianti_Guasto")
    anno_riferimento = 2025
    intestazioni_k2 = ["EDIFICIO", "N_IMPIANTI_TOTALI", f"Impianti_con_guasto_{anno_riferimento}",
                        f"Perc_impianti_con_guasto_{anno_riferimento}"]
    for c, nome in enumerate(intestazioni_k2):
        ws_k2.write(0, c, nome, fmt_header)

    for i, edificio in enumerate(edifici):
        r = i + 1
        ws_k2.write(r, 0, edificio)
        ws_k2.write_formula(r, 1, f"=VLOOKUP(A{r+1},Anagrafica_Impianti!$A:$B,2,0)")
        ws_k2.write_formula(
            r, 2,
            f'=SUMIFS(Base_ODL!$L$2:$L${ultima_riga},Base_ODL!$B$2:$B${ultima_riga},A{r+1},'
            f'Base_ODL!$I$2:$I${ultima_riga},{anno_riferimento})'
        )
        ws_k2.write_formula(r, 3, f"=ROUND(C{r+1}/B{r+1}*100,1)", fmt_perc)
    ws_k2.set_column("A:A", 25)

    # ==========================
    # FOGLIO KPI3 - Riepilogo recidivita' per anno (formule live, soglia parametrica)
    # ==========================
    ws_k3 = workbook.add_worksheet("KPI3_Riepilogo_Recidivita")
    intestazioni_k3 = ["Anno", "Impianti_con_guasto_totali", "Impianti_recidivi",
                        "Perc_impianti_recidivi", "ODL_totali_anno",
                        "ODL_generati_da_recidivi", "Perc_ODL_da_recidivi"]
    for c, nome in enumerate(intestazioni_k3):
        ws_k3.write(0, c, nome, fmt_header)

    for i, anno in enumerate(ANNI_INTERESSE):
        r = i + 1
        ws_k3.write(r, 0, anno)
        ws_k3.write_formula(
            r, 1, f"=SUMIFS(Base_ODL!$L$2:$L${ultima_riga},Base_ODL!$I$2:$I${ultima_riga},A{r+1})"
        )
        ws_k3.write_formula(
            r, 2, f"=SUMIFS(Base_ODL!$N$2:$N${ultima_riga},Base_ODL!$I$2:$I${ultima_riga},A{r+1})"
        )
        ws_k3.write_formula(r, 3, f"=ROUND(C{r+1}/B{r+1}*100,1)", fmt_perc)
        ws_k3.write_formula(
            r, 4, f"=COUNTIFS(Base_ODL!$I$2:$I${ultima_riga},A{r+1})"
        )
        ws_k3.write_formula(
            r, 5, f"=SUMIFS(Base_ODL!$M$2:$M${ultima_riga},Base_ODL!$I$2:$I${ultima_riga},A{r+1})"
        )
        ws_k3.write_formula(r, 6, f"=ROUND(F{r+1}/E{r+1}*100,1)", fmt_perc)

    workbook.close()
    print(f"Report live salvato: {FILE_OUTPUT}")
    print(f"Righe Base_ODL: {n}")
    print(f"Soglia recidivita' (modificabile in Parametri!B1): {SOGLIA_RECIDIVITA_DEFAULT}")


if __name__ == "__main__":
    main()
