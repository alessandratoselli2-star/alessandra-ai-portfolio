"""
M0 - Generatore dataset sintetico
Scenario: Facility Management B2B fittizio (Italia)
Struttura generica: EDIFICIO / IMPIANTO / TIPO_GUASTO

Include imperfezioni INTENZIONALI, utili per la fase M1 (Data Quality):
- valori mancanti in alcune colonne
- formati data incoerenti (misti: dd/mm/yyyy, yyyy-mm-dd, dd-mm-yy)
- spazi/maiuscole incoerenti nei nomi edificio
- alcuni duplicati esatti
- alcuni IMPIANTO con codice placeholder ('-', 'NA', vuoto)
"""

import random
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)

# ==========================
# ANAGRAFICA EDIFICI (fittizia)
# ==========================

EDIFICI = [
    ("TORRE NORD MILANO", 320),
    ("TORRE SUD MILANO", 270),
    ("CAMPUS TORINO EST", 210),
    ("CAMPUS TORINO OVEST", 160),
    ("HUB LOGISTICO BOLOGNA", 400),
    ("SEDE BRESCIA", 130),
    ("POLO PADOVA", 180),
    ("CENTRO DIREZIONALE ROMA", 350),
    ("STABILIMENTO VERONA", 230),
    ("FILIALE FIRENZE", 110),
]

TIPI_GUASTO = [
    "Climatizzazione", "Elettrico", "Idraulico", "Ascensori",
    "Antincendio", "Illuminazione", "Sicurezza accessi", "Building Automation"
]

TECNICI = ["Rossi", "Bianchi", "Verdi", "Colombo", "Ferrari", "Romano", "Gallo", "Conti"]
FORNITORI = ["TecnoService Srl", "ImpiantiPro SpA", "FM Solutions", "Manutenzioni Italia Srl"]
STATUS = ["Chiuso", "In corso", "Sospeso", "Chiuso", "Chiuso"]  # 'Chiuso' piu' frequente

DATA_INIZIO = datetime(2024, 1, 1)
DATA_FINE = datetime(2026, 8, 31)
N_RIGHE = 4200


def data_casuale():
    delta = (DATA_FINE - DATA_INIZIO).days
    return DATA_INIZIO + timedelta(days=random.randint(0, delta))


def formatta_data_sporca(dt: datetime) -> str:
    """Restituisce la data in uno tra piu' formati, per simulare incoerenza reale."""
    formati = [
        lambda d: d.strftime("%d/%m/%Y"),
        lambda d: d.strftime("%Y-%m-%d"),
        lambda d: d.strftime("%d-%m-%y"),
        lambda d: d.strftime("%d.%m.%Y"),
    ]
    scelta = random.choices(formati, weights=[50, 25, 15, 10])[0]
    return scelta(dt)


def genera_impianto_id(edificio: str, n_impianti: int, indice_edificio: int) -> str:
    prefisso = "".join(w[0] for w in edificio.split()[:2]).upper()
    numero = random.randint(1, n_impianti)
    # L'indice edificio garantisce codici univoci anche tra edifici con prefisso uguale
    # (es. 'Campus Torino Est' e 'Campus Torino Ovest' generano entrambi 'CT')
    return f"IMP-{prefisso}{indice_edificio}-{numero:03d}"


def sporca_nome_edificio(nome: str) -> str:
    """Introduce incoerenze di maiuscole/spazi in una minoranza di righe."""
    r = random.random()
    if r < 0.08:
        return nome.title()
    if r < 0.14:
        return f" {nome} "
    if r < 0.18:
        return nome.lower()
    return nome


righe = []
for i in range(N_RIGHE):
    edificio_base, n_impianti = random.choice(EDIFICI)
    indice_edificio = [e[0] for e in EDIFICI].index(edificio_base)
    dt = data_casuale()

    # Quota di impianti "problematici": una minoranza di ODL pesca da un pool
    # ristretto e fisso di impianti, che quindi accumulano piu' interventi.
    # La maggioranza degli ODL invece pesca dall'intero parco impianti,
    # dove la probabilita' di ripetersi sullo stesso impianto e' bassa.
    if random.random() < 0.15:
        impianto = genera_impianto_id(edificio_base, min(n_impianti, 8), indice_edificio)  # pool ristretto -> ripetizioni
    else:
        impianto = genera_impianto_id(edificio_base, n_impianti, indice_edificio)

    riga = {
        "ID_ODL": f"ODL{100000 + i}",
        "EDIFICIO": sporca_nome_edificio(edificio_base),
        "IMPIANTO": impianto,
        "TIPO_GUASTO": random.choice(TIPI_GUASTO),
        "DATA_CREAZIONE": formatta_data_sporca(dt),
        "STATUS": random.choice(STATUS),
        "TECNICO": random.choice(TECNICI),
        "FORNITORE": random.choice(FORNITORI),
    }
    righe.append(riga)

df = pd.DataFrame(righe)

# --- Imperfezioni aggiuntive intenzionali ---

# 1) Valori mancanti sparsi in alcune colonne
for col, frac in [("TECNICO", 0.04), ("FORNITORE", 0.03), ("STATUS", 0.02)]:
    idx = df.sample(frac=frac, random_state=1).index
    df.loc[idx, col] = None

# 2) IMPIANTO con placeholder invece di codice valido
idx_placeholder = df.sample(frac=0.015, random_state=2).index
df.loc[idx_placeholder, "IMPIANTO"] = random.choice(["-", "NA", ""])

# 3) Duplicati esatti (simulano doppio inserimento da parte del tecnico)
duplicati = df.sample(frac=0.02, random_state=3)
df = pd.concat([df, duplicati], ignore_index=True)

# 4) Righe con DATA_CREAZIONE mancante o palesemente errata
idx_data_mancante = df.sample(frac=0.01, random_state=4).index
df.loc[idx_data_mancante, "DATA_CREAZIONE"] = None

idx_data_errata = df.sample(frac=0.005, random_state=5).index
df.loc[idx_data_errata, "DATA_CREAZIONE"] = "31/02/2025"  # data inesistente

df = df.sample(frac=1, random_state=6).reset_index(drop=True)  # mescola l'ordine

# ==========================
# FOGLIO ANAGRAFICA IMPIANTI (equivalente a "Consistenze")
# ==========================

anagrafica = pd.DataFrame(EDIFICI, columns=["EDIFICIO", "N_IMPIANTI_TOTALI"])

# ==========================
# EXPORT
# ==========================

FILE_OUT = "dataset_sintetico_fm.xlsx"
with pd.ExcelWriter(FILE_OUT, engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="ODL", index=False)
    anagrafica.to_excel(writer, sheet_name="Anagrafica_Impianti", index=False)

print(f"Dataset generato: {FILE_OUT}")
print(f"Righe totali (incluse imperfezioni): {len(df)}")
print(f"Edifici: {len(EDIFICI)}")
print("\nAnteprima:")
print(df.head(10).to_string())
print("\nValori mancanti per colonna:")
print(df.isna().sum())
