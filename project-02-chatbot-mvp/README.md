Project 02 — Agente conversazionale sui dati (MVP)

Un assistente conversazionale che risponde in linguaggio naturale a domande sui dati operativi di Project 01, senza che chi lo usa debba aprire un file Excel o sapere cosa sia un KPI.

Nota sui dati: stesso dataset sintetico di Project 01. Nessun dato aziendale reale.

Il problema che affronta

Project 01 produce un report periodico — utile, ma richiede che qualcuno lo apra, lo legga, e sappia dove guardare. Project 02 capovolge l'approccio: chi ha bisogno di un'informazione la chiede direttamente, in linguaggio naturale, e la ottiene subito. È il passaggio da "reportistica che qualcuno distribuisce" a "self-service analytics" — chi ha bisogno di un dato se lo prende da solo.

Perché una versione MVP, e non un chatbot standalone

Un chatbot "vero" (accessibile da chiunque via un link web, senza passare da un account Claude) richiederebbe un'interfaccia web, una chiave API, e un hosting dedicato — una complessità tecnica e di tempo non giustificata per validare l'idea. Questa versione MVP usa Claude Projects: nessun codice, nessun hosting, stesso principio di funzionamento (i dati come "conoscenza" consultabile in linguaggio naturale). Non è pubblicamente accessibile a chiunque, ma dimostra il concetto ed è la base naturale per un'eventuale versione più estesa in futuro.

Come funziona
I dati calcolati di Project 01 (KPI, top impianti critici, executive summary) sono raccolti in un unico file di testo leggibile: knowledge_base_project01.md. Non i file Excel originali: un Claude Project legge il contenuto dei file ma non esegue formule, quindi i numeri devono essere già "risolti" in tabelle testuali per garantire risposte corrette.
Il file viene caricato come conoscenza in un Claude Project dedicato.
Istruzioni personalizzate (vedi sotto) vincolano l'assistente a usare solo i numeri presenti nella conoscenza, senza stimarli o inventarli.
Istruzioni personalizzate usate
Sei un assistente che risponde a domande sui dati di performance operativa
del Project 01 (Facility Management, dati sintetici). Usa SEMPRE i numeri
esatti presenti nella conoscenza del progetto, non stimarli. Rispondi in
linguaggio manageriale, conciso, citando i numeri specifici. Se una domanda
richiede un dato non presente nella conoscenza, dillo chiaramente invece di
inventare una risposta plausibile.
Esempi di domande testate
"Quali sono i 3 edifici con la percentuale più alta di impianti guasti nel 2025?"
"Qual è il trend della recidività negli ultimi 3 anni?"

(screenshot delle risposte in screenshots/)
