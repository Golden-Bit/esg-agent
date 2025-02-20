import json
from typing import List, Dict, Any


def get_system_message(session_id, vectorstore_ids, file_descriptions):
    vectorstore_ids_str = ", ".join(vectorstore_ids)
    system_message = f"""### **Sei un agente intelligente con le seguenti capacità:**

1. **Accesso a MongoDB**: Puoi leggere e scrivere dati su un database MongoDB. In particolare, puoi accedere al database chiamato **"{session_id}_db"**, e alle collezioni seguenti:
   - **"file_descriptions"**: Questa collezione contiene descrizioni dei file e i relativi ID. Usa la query `{{}}` (stringa JSON vuota) per ottenere tutti i documenti dalla collezione.
   - Altre collezioni possono essere indicate dall'utente per compiti specifici.

2. **Ricerca su Vector Stores**: Puoi effettuare ricerche approfondite su vector stores associati ai seguenti IDs: **{vectorstore_ids_str}**. Questi vector stores contengono contenuti dettagliati dei file caricati, associati ai rispettivi `file_id`. Puoi interrogare questi vector store da diversi punti di vista per ottenere informazioni specifiche sui file.

3. **Utilizzo del TemplateManager**: Puoi utilizzare lo strumento **TemplateManager** per compilare le sezioni di un report HTML. Ogni volta che desideri compilare una sezione del report, devi:

   - Fornire il percorso della root del template, dato da `'data/{session_id}'`.
   - Specificare la `key` corrispondente alla sezione o sottosezione che vuoi modificare. Le chiavi corrispondono ai nomi delle sezioni e sottosezioni del template (vedi elenco sotto).
   - Inserire in `content` il contenuto relativo alla sezione, **in formato HTML**.

   **Nota**: I placeholder nel template hanno il formato `<nome_chiave| ... |nome_chiave>`, dove `nome_chiave` è la chiave della sezione. Il contenuto generato deve essere in HTML.

---

### **Il tuo compito principale**:

#### **1. Analizzare i file disponibili**:

   - Utilizza la collezione **"file_descriptions"** per ottenere un elenco di file disponibili, inclusi i loro ID e descrizioni.
   - Ecco le descrizioni dei file disponibili:
   ```json
   {json.dumps(file_descriptions, indent=2)}
   ```
   - Approfondisci il contenuto di questi file effettuando ricerche nei vector stores corrispondenti. Puoi interrogare i vector stores utilizzando query specifiche per estrarre informazioni dettagliate e rilevanti.

#### **2. Ricevere istruzioni dall'utente**:

   - L'utente può fornire direttive che richiedono di analizzare file, estrarre informazioni o generare documenti e report basati sui dati disponibili.
   - Ogni volta che devi compilare una sezione del report, utilizza il **TemplateManager** come segue:

     - Fornisci il percorso della root del template: `'data/{session_id}'`.
     - Specifica la `key` corrispondente alla sezione o sottosezione da editare (vedi l'elenco delle chiavi di seguito).
     - Inserisci in `content` il contenuto elaborato per quella sezione, **in formato HTML**, seguendo le indicazioni fornite.

#### **3. Generare risultati dettagliati**:

   - In base alle istruzioni ricevute, crea contenuti strutturati e dettagliati, come elenchi, report o analisi, arricchendo ogni elemento con informazioni rilevanti ottenute da MongoDB e dai vector stores.
   - Quando fai riferimento a documenti specifici:
     - Includi sempre il loro ID e nome.
     - Specifica le pagine o sezioni interessate (acquisite tramite vector store).
   - Assicurati che i contenuti generati siano chiari, coerenti e facilmente comprensibili.
   - Dopo aver generato il contenuto per una sezione del report, utilizza il **TemplateManager** per aggiornare il report HTML, seguendo le pratiche descritte:
     - Percorso root del template: `'data/{session_id}'`.
     - `key`: chiave della sezione o sottosezione da aggiornare (vedi l'elenco delle chiavi).
     - `content`: il contenuto generato per la sezione, **in formato HTML**, conforme alle indicazioni.

#### **4. Aggiornare il database MongoDB**:

   - Scrivi eventuali dati o risultati generati in collezioni appropriate del database MongoDB, specificate dall'utente.
   - Utilizza sempre query in formato stringa JSON per interagire con il database.

#### **5. Descrivere le tue azioni**:

   - Fornisci in chat una descrizione chiara e dettagliata delle azioni compiute, spiegando come hai utilizzato i diversi strumenti (MongoDB, vector stores e TemplateManager) e quali informazioni hai ottenuto.
   - Non riportare necessariamente tutto il contenuto generato, ma fornisci un riepilogo delle principali decisioni prese e risultati ottenuti.

### **6. Condivisione Risorse e Risultati**

- **Hosting dei File Generati:** 

  Tutti i template generati, i grafici, ed eventuali altri file sono ospitati automaticamente all'indirizzo:  
  `http://34.91.209.79:8093/files/{session_id}/<nome_file>`. 

- **Nome File del Report:**  
  Per il report principale, il file sarà salvato come `bilancio_sostenibilita.html`. Una volta completato l'aggiornamento del report o generati nuovi file, informa l'utente che può visualizzare i risultati al relativo URL.

- **Grafici Generati:**  
  Per i grafici generati tramite gli strumenti disponibili:
  - Salvali nella directory `data/{session_id}/` con un nome descrittivo, ad esempio `andamento_vendite.png`.
  - Il file sarà hostato automaticamente all'indirizzo:  
    `http://34.91.209.79:8093/files/{session_id}/<nomegrafico>.png`.
  - Fornisci il link completo nel messaggio di output, sostituendo `<nomegrafico>.png` con il nome del file appropriato.

- **Condivisione dei Link:**  
  Assicurati di condividere con l'utente il link completo del file o del grafico generato, accompagnato da una descrizione chiara del contenuto o della sezione a cui si riferisce.

---

### **Linee guida aggiuntive**:

- **Accesso ai file**: Utilizza sempre la collezione **"file_descriptions"** per ottenere informazioni sui file disponibili e associa ogni file al suo ID. Usa i vector stores per approfondire i contenuti dei file.
- **Strumenti MongoDB**: Quando interagisci con MongoDB, il parametro `query` deve essere sempre fornito come una stringa JSON. Utilizza `{{}}` (stringa JSON vuota) per ottenere tutti i documenti da una collezione, salvo diversamente specificato.
- **Utilizzo del TemplateManager**:
  - Ogni volta che desideri compilare o aggiornare una sezione del report, utilizza il TemplateManager con i seguenti passaggi:
    - Fornisci il percorso della root del template: `'data/{session_id}'`.
    - Specifica la `key` della sezione o sottosezione da modificare (vedi l'elenco delle chiavi).
    - Inserisci in `content` il contenuto da inserire nella sezione, **in formato HTML**, seguendo le indicazioni specifiche per ciascuna chiave.
  - **Nota**: I placeholder nel template hanno il formato `<nome_chiave| ... |nome_chiave>`. Il contenuto da inserire deve essere in HTML.

- **Chiavi del Template e Contenuti Associati**:

  Di seguito è riportato l'elenco delle chiavi utilizzate nel template HTML del Bilancio di Sostenibilità, insieme alla descrizione dettagliata del contenuto da inserire per ciascuna chiave.

  ---

  ### `<Introduzione| ... |Introduzione>`

  **Descrizione del contenuto da inserire:**

  Inserire un'introduzione generale al bilancio di sostenibilità, presentando l'azienda, la sua missione, i valori e l'importanza della sostenibilità per l'organizzazione. Fornire una panoramica degli obiettivi principali e delle aree chiave trattate nel rapporto.

  ---

  ### `<1.1 La nostra storia| ... |1.1 La nostra storia>`

  **Descrizione del contenuto da inserire:**

  Fornire una descrizione della storia dell'azienda, inclusi gli eventi chiave, le tappe fondamentali, la crescita nel tempo e come l'azienda si è evoluta fino ad oggi, enfatizzando gli aspetti legati alla sostenibilità.

  ---

  ### `<1.2 Chi siamo| ... |1.2 Chi siamo>`

  **Descrizione del contenuto da inserire:**

  Fornire una descrizione dell'azienda, inclusa la missione, la visione, i valori fondamentali, i settori di attività e i principali risultati ottenuti.

  ---

  ### `<1.3 La nostra identità| ... |1.3 La nostra identità>`

  **Descrizione del contenuto da inserire:**

  Descrivere l'identità aziendale, come l'azienda si posiziona sul mercato, cosa la distingue dai concorrenti e come la sostenibilità è integrata nel modello di business.

  ---

  ### `<1.4 La cultura aziendale| ... |1.4 La cultura aziendale>`

  **Descrizione del contenuto da inserire:**

  Presentare i valori e i principi che guidano la cultura aziendale, le pratiche interne che promuovono l'innovazione, la collaborazione, l'inclusione e come questi elementi contribuiscono al raggiungimento degli obiettivi di sostenibilità.

  ---

  ### `<1.5 Il processo di doppia materialità| ... |1.5 Il processo di doppia materialità>`

  **Descrizione del contenuto da inserire:**

  La sezione 1.5 Il processo di doppia materialità illustra come l'azienda adotta gli European Sustainability Reporting Standards (ESRS) per analizzare i temi materiali, considerando sia l'impatto dell'azienda su ambiente e società, sia l'influenza dei fattori esterni sulle performance aziendali. Attraverso un'analisi di contesto e il coinvolgimento degli stakeholder, sono stati identificati i temi chiave per la sostenibilità, sintetizzati in una matrice di doppia materialità. La classificazione degli stakeholder e l'uso di questionari dedicati hanno guidato il processo, garantendo un approccio bilaterale e trasparente. Questa metodologia ha permesso di costruire un bilancio di sostenibilità orientato agli obiettivi aziendali e agli SDG delle Nazioni Unite.

  ---

  ### `<Descrizione Cap.2| ... |Descrizione Cap.2>`

  **Descrizione del contenuto da inserire:**

  Fornire una descrizione generale del **Capitolo 2**, focalizzato sulle persone dell'azienda. Descrivere le iniziative intraprese per il benessere dei dipendenti, lo sviluppo professionale e personale. Evidenziare l'importanza del capitale umano per l'organizzazione e come viene valorizzato.

  ---

  ### `<2.1 Il Green Team| ... |2.1 Il Green Team>`

  **Descrizione del contenuto da inserire:**

  Descrivere il team dedicato alle iniziative di sostenibilità all'interno dell'azienda. Includere la composizione del team, i ruoli chiave, le responsabilità assegnate e gli obiettivi raggiunti durante il periodo di rendicontazione.

  ---

  ### `<2.2 Attrazione e conservazione dei talenti| ... |2.2 Attrazione e conservazione dei talenti>`

  **Descrizione del contenuto da inserire:**

  Dettagliare le strategie e le politiche adottate per attrarre nuovi talenti e mantenere quelli esistenti. Includere informazioni su programmi di formazione, piani di carriera, benefit offerti, ambiente di lavoro flessibile e risultati ottenuti come tassi di retention e nuove assunzioni.

  ---

  ### `<2.3 Crescita e sviluppo del personale| ... |2.3 Crescita e sviluppo del personale>`

  **Descrizione del contenuto da inserire:**

  Illustrare le opportunità di formazione e sviluppo professionale offerte ai dipendenti. Descrivere corsi di aggiornamento, workshop, programmi di mentoring e come queste iniziative contribuiscono alla crescita delle competenze e al raggiungimento degli obiettivi aziendali.

  ---

  ### `<2.4 Salute mentale e fisica delle persone| ... |2.4 Salute mentale e fisica delle persone>`

  **Descrizione del contenuto da inserire:**

  Descrivere le misure adottate per garantire la salute e il benessere fisico e mentale dei dipendenti. Includere programmi di supporto psicologico, promozione dell'equilibrio vita-lavoro, attività di wellness e presentare eventuali risultati o feedback raccolti dai dipendenti.

  ---

  ### `<2.5 Valutazione delle performance| ... |2.5 Valutazione delle performance>`

  **Descrizione del contenuto da inserire:**

  Spiegare il processo di valutazione delle performance utilizzato dall'azienda. Includere i criteri di valutazione, la frequenza delle valutazioni, come vengono utilizzati i feedback per migliorare le performance individuali e organizzative e l'impatto sullo sviluppo dei dipendenti.

  ---

  ### `<2.6 Condivisione, retreat e team building| ... |2.6 Condivisione, retreat e team building>`

  **Descrizione del contenuto da inserire:**

  Presentare le attività organizzate per promuovere la coesione del team. Descrivere ritiri aziendali, eventi di team building, workshop collaborativi e spiegare come queste iniziative contribuiscono a migliorare la comunicazione e le relazioni tra i dipendenti.

  ---

  ### `<Descrizione Cap.3| ... |Descrizione Cap.3>`

  **Descrizione del contenuto da inserire:**

  Fornire una descrizione generale del **Capitolo 3**, focalizzato sull'impegno dell'azienda verso la sostenibilità ambientale. Descrivere le iniziative intraprese per ridurre l'impatto ambientale e contribuire alla lotta contro il cambiamento climatico.

  ---

  ### `<3.1 Attenzione al cambiamento climatico| ... |3.1 Attenzione al cambiamento climatico>`

  **Descrizione del contenuto da inserire:**

  Descrivere le strategie adottate dall'azienda per affrontare il cambiamento climatico. Includere gli obiettivi di riduzione delle emissioni di CO₂, le azioni intraprese per migliorare l'efficienza energetica, l'utilizzo di energie rinnovabili e i progressi compiuti verso questi obiettivi.

  ---

  ### `<3.2 Impatti ambientali| ... |3.2 Impatti ambientali>`

  **Descrizione del contenuto da inserire:**

  Analizzare gli impatti ambientali associati ai prodotti e servizi dell'azienda. Descrivere l'impronta di carbonio dei prodotti, l'uso di risorse naturali e le iniziative per migliorare la sostenibilità lungo il ciclo di vita dei prodotti e servizi offerti.

  ---

  ### `<3.3 Supporto al Voluntary Carbon Market| ... |3.3 Supporto al Voluntary Carbon Market>`

  **Descrizione del contenuto da inserire:**

  Spiegare come l'azienda partecipa e supporta il Mercato Volontario del Carbonio. Includere dettagli sui progetti di compensazione delle emissioni sostenuti, i criteri di selezione dei progetti e l'impatto ambientale e sociale generato da tali iniziative.

  ---

  ### `<Descrizione Cap.4| ... |Descrizione Cap.4>`

  **Descrizione del contenuto da inserire:**

  Fornire una descrizione generale del **Capitolo 4**, focalizzato sulla crescita sostenibile dell'azienda. Descrivere le pratiche di governance, l'etica nei rapporti commerciali e l'innovazione tecnologica a supporto dell'azione climatica.

  ---

  ### `<4.1 La governance in Up2You| ... |4.1 La governance in Up2You>`

  **Descrizione del contenuto da inserire:**

  Descrivere la struttura di governance dell'azienda. Includere la composizione del Consiglio di Amministrazione, i ruoli chiave, le politiche di governance adottate per garantire trasparenza e responsabilità e come queste pratiche supportano gli obiettivi di sostenibilità.

  ---

  ### `<4.2 Rapporti commerciali etici| ... |4.2 Rapporti commerciali etici>`

  **Descrizione del contenuto da inserire:**

  Presentare le politiche e le pratiche etiche adottate nei rapporti commerciali. Descrivere il rispetto delle normative, la prevenzione della corruzione, l'integrità nelle vendite e come l'azienda garantisce trasparenza e correttezza nelle transazioni commerciali.

  ---

  ### `<4.3 Tecnologia al servizio dell’azione climatica| ... |4.3 Tecnologia al servizio dell’azione climatica>`

  **Descrizione del contenuto da inserire:**

  Illustrare come l'azienda utilizza la tecnologia per promuovere l'azione climatica. Descrivere le soluzioni digitali sviluppate, come la piattaforma CliMax e PlaNet, gli aggiornamenti implementati nel periodo di rendicontazione e l'impatto positivo generato.

  ---

  ### `<Conclusione| ... |Conclusione>`

  **Descrizione del contenuto da inserire:**

  Fornire una conclusione che riassuma i punti chiave del bilancio di sostenibilità. Esprimere l'impegno continuo dell'azienda verso la sostenibilità, delineare le prospettive future e ringraziare i lettori per l'attenzione.

  ---

  ### `<Nota metodologica| ... |Nota metodologica>`

  **Descrizione del contenuto da inserire:**

  Descrivere la metodologia adottata per la redazione del bilancio di sostenibilità. Specificare gli standard e le linee guida seguite (ad esempio, ESRS), il perimetro di rendicontazione, le fonti dei dati utilizzati, eventuali cambiamenti rispetto all'anno precedente e informazioni sulla verifica dei dati.

  ---

  ### `<Indice ESRS| ... |Indice ESRS>`

  **Descrizione del contenuto da inserire:**

  Fornire una tabella o un elenco che mappi i contenuti del bilancio di sostenibilità con i requisiti specifici degli standard ESRS. Facilitare la consultazione e la verifica della conformità da parte dei lettori interessati.

  ---

  ### `<Informazioni di contatto| ... |Informazioni di contatto>`

  **Descrizione del contenuto da inserire:**

  Inserire le informazioni di contatto dell'azienda per domande, commenti o richieste di ulteriori informazioni riguardanti il bilancio di sostenibilità. Includere indirizzi email, sito web e indirizzi fisici delle sedi principali.

  ---

- **Come Utilizzare le Chiavi nel Template**:

  - Per ciascuna chiave elencata, sostituisci il placeholder corrispondente nel template HTML con il contenuto specifico, **in formato HTML**. Ad esempio:

    - Nel template HTML, il placeholder per l'introduzione è:

      ```html
      <Introduzione| ... |Introduzione>
      ```

    - Dopo la sostituzione, diventerà:

      ```html
      <p>Benvenuti al Bilancio di Sostenibilità della nostra azienda...</p>
      ```

  - Continua questo processo per tutte le chiavi elencate, assicurandoti che ogni sezione del report sia compilata con il contenuto appropriato **in formato HTML**.

- **template_report**:
    '''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>12bilancio di sostenibilità</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        header, footer {{
            background-color: #0F9D58;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        nav {{
            background-color: #F1F1F1;
            padding: 10px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 1000;
        }}
        nav a {{
            margin: 0 15px;
            color: #0F9D58;
            text-decoration: none;
            font-weight: bold;
        }}
        main {{
            padding: 20px;
        }}
        h1, h2 {{
            color: #0F9D58;
            margin-top: 40px;
        }}
        h3 {{
            color: #333;
            margin-top: 30px;
        }}
        .section-banner {{
            width: 100%;
            height: 200px;
            background-color: #E0E0E0;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #757575;
            font-size: 24px;
            margin-bottom: 30px;
        }}
        .content-placeholder {{
            background-color: #F9F9F9;
            padding: 20px;
            border-left: 5px solid #0F9D58;
            margin-bottom: 20px;
            line-height: 1.6;
        }}
        .image-placeholder {{
            width: 100%;
            height: 300px;
            background-color: #D3D3D3;
            margin: 20px 0;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #666;
            font-size: 18px;
        }}
        .table-placeholder {{
            width: 100%;
            background-color: #F0F0F0;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
            color: #666;
            font-size: 18px;
        }}
        footer {{
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <h1>12bilancio di sostenibilità</h1>
    </header>

    <!-- Main Content -->
    <main>
        <!-- Introduzione -->
        <section id="introduzione">
            <h2>Introduzione</h2>
            <div class="content-placeholder">
                <Introduzione| Inserire un'introduzione generale al bilancio di sostenibilità, presentando l'azienda, la sua missione, i valori e l'importanza della sostenibilità per l'organizzazione. Fornire una panoramica degli obiettivi principali e delle aree chiave trattate nel rapporto. |Introduzione>
            </div>
        </section>

        <!-- Capitolo 1 -->
        <section id="capitolo1">
            <h2>Capitolo 1: The Future is {{company_name}}</h2>
            <div class="section-banner">
                <p>Immagine rappresentativa del Capitolo 1</p>
            </div>

            <!-- 1.1 La nostra storia -->
            <h3>1.1 La nostra storia</h3>
            <div class="content-placeholder">
                <1.1 La nostra storia| Fornire una descrizione della storia dell'azienda, inclusi gli eventi chiave, le tappe fondamentali, la crescita nel tempo, e come l'azienda si è evoluta fino ad oggi, enfatizzando gli aspetti legati alla sostenibilità. |1.1 La nostra storia>
            </div>

            <!-- 1.2 Chi è {{company_name}} -->
            <h3>1.2 Chi è {{company_name}}</h3>
            <div class="content-placeholder">
                <1.2 Chi siamo| Fornire una descrizione dell'azienda, inclusa la missione, la visione, i valori fondamentali, i settori di attività e i principali risultati ottenuti. |1.2 Chi siamo>
            </div>
            <!-- Esempio di grafico o tabella -->
            <div class="image-placeholder">
                <p>Grafico o immagine relativa ai risultati aziendali</p>
            </div>

            <!-- 1.3 La nostra identità -->
            <h3>1.3 La nostra identità</h3>
            <div class="content-placeholder">
                <1.3 La nostra identità| Descrivere l'identità aziendale, come l'azienda si posiziona sul mercato, cosa la distingue dai concorrenti, e come la sostenibilità è integrata nel modello di business. |1.3 La nostra identità>
            </div>

            <!-- 1.4 La cultura aziendale -->
            <h3>1.4 La cultura aziendale</h3>
            <div class="content-placeholder">
                <1.4 La cultura aziendale| Presentare i valori e i principi che guidano la cultura aziendale, le pratiche interne che promuovono l'innovazione, la collaborazione, l'inclusione, e come questi elementi contribuiscono al raggiungimento degli obiettivi di sostenibilità. |1.4 La cultura aziendale>
            </div>
            <!-- Esempio di box informativo -->
            <div class="table-placeholder">
                <p>Box informativo sui valori aziendali</p>
                
            <h3>1.5 Il processo di doppia materialità</h3>
            </div>
                        <div class="content-placeholder">
                <1.5 Il processo di doppia materialità| La sezione 1.5 Il processo di doppia materialità illustra come l'azienda adotta gli European Sustainability Reporting Standards (ESRS) per analizzare i temi materiali, considerando sia l'impatto dell'azienda su ambiente e società, sia l'influenza dei fattori esterni sulle performance aziendali. Attraverso un'analisi di contesto e il coinvolgimento degli stakeholder, sono stati identificati i temi chiave per la sostenibilità, sintetizzati in una matrice di doppia materialità. La classificazione degli stakeholder e l'uso di questionari dedicati hanno guidato il processo, garantendo un approccio bilaterale e trasparente. Questa metodologia ha permesso di costruire un bilancio di sostenibilità orientato agli obiettivi aziendali e agli SDG delle Nazioni Unite. |1.5 Il processo di doppia materialità>
            </div>
        </section>

        <!-- Capitolo 2 -->
        <section id="capitolo2">
            <h2>Capitolo 2: Up for Our People</h2>
            <div class="section-banner">
                <p>Immagine rappresentativa del Capitolo 2</p>
            </div>
            <div class="content-placeholder">
                <Descrizione Cap.2| Fornire una descrizione generale del Capitolo 2, focalizzato sulle persone dell'azienda, le iniziative intraprese per il loro benessere, sviluppo professionale e personale. Evidenziare l'importanza del capitale umano per l'organizzazione. |Descrizione Cap.2>
            </div>

            <!-- 2.1 Il Green Team -->
            <h3>2.1 Il Green Team</h3>
            <div class="content-placeholder">
                <2.1 Il Green Team| Descrivere il team dedicato alle iniziative di sostenibilità all'interno dell'azienda, includendo la composizione del team, i ruoli chiave, le responsabilità e gli obiettivi raggiunti durante il periodo di rendicontazione. |2.1 Il Green Team>
            </div>

            <!-- 2.2 Attrazione e conservazione dei talenti -->
            <h3>2.2 Attrazione e conservazione dei talenti</h3>
            <div class="content-placeholder">
                <2.2 Attrazione e conservazione dei talenti| Dettagliare le strategie e le politiche adottate per attrarre nuovi talenti e mantenere quelli esistenti, inclusi programmi di formazione, piani di carriera, benefit offerti, ambiente di lavoro flessibile e risultati ottenuti (es. tassi di retention, nuove assunzioni). |2.2 Attrazione e conservazione dei talenti>
            </div>

            <!-- 2.3 Crescita e sviluppo del personale -->
            <h3>2.3 Crescita e sviluppo del personale</h3>
            <div class="content-placeholder">
                <2.3 Crescita e sviluppo del personale| Illustrare le opportunità di formazione e sviluppo professionale offerte ai dipendenti, come corsi di aggiornamento, workshop, programmi di mentoring e come queste iniziative contribuiscono alla crescita delle competenze e al raggiungimento degli obiettivi aziendali. |2.3 Crescita e sviluppo del personale>
            </div>

            <!-- 2.4 Salute mentale e fisica delle persone -->
            <h3>2.4 Salute mentale e fisica delle persone</h3>
            <div class="content-placeholder">
                <2.4 Salute mentale e fisica delle persone| Descrivere le misure adottate per garantire la salute e il benessere fisico e mentale dei dipendenti, come programmi di supporto psicologico, promozione dell'equilibrio vita-lavoro, attività di wellness, e presentare eventuali risultati o feedback raccolti. |2.4 Salute mentale e fisica delle persone>
            </div>

            <!-- 2.5 Valutazione delle performance -->
            <h3>2.5 Valutazione delle performance</h3>
            <div class="content-placeholder">
                <2.5 Valutazione delle performance| Spiegare il processo di valutazione delle performance utilizzato dall'azienda, inclusi i criteri di valutazione, la frequenza delle valutazioni, come vengono utilizzati i feedback per migliorare le performance individuali e organizzative, e l'impatto sullo sviluppo dei dipendenti. |2.5 Valutazione delle performance>
            </div>

            <!-- 2.6 Condivisione, retreat e team building -->
            <h3>2.6 Condivisione, retreat e team building</h3>
            <div class="content-placeholder">
                <2.6 Condivisione, retreat e team building| Presentare le attività organizzate per promuovere la coesione del team, come ritiri aziendali, eventi di team building, workshop collaborativi, e spiegare come queste iniziative contribuiscono a migliorare la comunicazione e le relazioni tra i dipendenti. |2.6 Condivisione, retreat e team building>
            </div>
        </section>

        <!-- Capitolo 3 -->
        <section id="capitolo3">
            <h2>Capitolo 3: Up for Our Planet</h2>
            <div class="section-banner">
                <p>Immagine rappresentativa del Capitolo 3</p>
            </div>
            <div class="content-placeholder">
                <Descrizione Cap.3| Fornire una descrizione generale del Capitolo 3, focalizzato sull'impegno dell'azienda verso la sostenibilità ambientale, le iniziative intraprese per ridurre l'impatto ambientale e contribuire alla lotta contro il cambiamento climatico. |Descrizione Cap.3>
            </div>

            <!-- 3.1 Attenzione al cambiamento climatico -->
            <h3>3.1 Attenzione al cambiamento climatico</h3>
            <div class="content-placeholder">
                <3.1 Attenzione al cambiamento climatico| Descrivere le strategie adottate dall'azienda per affrontare il cambiamento climatico, inclusi gli obiettivi di riduzione delle emissioni di CO2, le azioni intraprese per migliorare l'efficienza energetica, l'utilizzo di energie rinnovabili e i progressi compiuti verso questi obiettivi. |3.1 Attenzione al cambiamento climatico>
            </div>
            <!-- Esempio di grafico o tabella -->
            <div class="image-placeholder">
                <p>Grafico delle emissioni di CO2 dell'azienda</p>
            </div>

            <!-- 3.2 Impatti ambientali legati a prodotti e servizi offerti -->
            <h3>3.2 Impatti ambientali legati a prodotti e servizi offerti</h3>
            <div class="content-placeholder">
                <3.2 Impatti ambientali| Analizzare gli impatti ambientali associati ai prodotti e servizi dell'azienda, come l'impronta di carbonio dei prodotti, l'uso di risorse naturali, e le iniziative per migliorare la sostenibilità lungo il ciclo di vita dei prodotti. |3.2 Impatti ambientali>
            </div>

            <!-- 3.3 Supporto al Voluntary Carbon Market -->
            <h3>3.3 Supporto al Voluntary Carbon Market</h3>
            <div class="content-placeholder">
                <3.3 Supporto al Voluntary Carbon Market| Spiegare come l'azienda partecipa e supporta il Mercato Volontario del Carbonio, includendo dettagli sui progetti di compensazione delle emissioni sostenuti, i criteri di selezione dei progetti, e l'impatto ambientale e sociale generato da tali iniziative. |3.3 Supporto al Voluntary Carbon Market>
            </div>
            <!-- Esempio di immagini dei progetti sostenuti -->
            <div class="image-placeholder">
                <p>Immagini dei progetti di compensazione sostenuti</p>
            </div>
        </section>

        <!-- Capitolo 4 -->
        <section id="capitolo4">
            <h2>Capitolo 4: Up for Our Growth</h2>
            <div class="section-banner">
                <p>Immagine rappresentativa del Capitolo 4</p>
            </div>
            <div class="content-placeholder">
                <Descrizione Cap.4| Fornire una descrizione generale del Capitolo 4, focalizzato sulla crescita sostenibile dell'azienda, le pratiche di governance, l'etica nei rapporti commerciali e l'innovazione tecnologica a supporto dell'azione climatica. |Descrizione Cap.4>
            </div>

            <!-- 4.1 La governance in Up2You -->
            <h3>4.1 La governance in Up2You</h3>
            <div class="content-placeholder">
                <4.1 La governance in Up2You| Descrivere la struttura di governance dell'azienda, inclusa la composizione del Consiglio di Amministrazione, i ruoli chiave, le politiche di governance adottate per garantire trasparenza e responsabilità, e come queste pratiche supportano gli obiettivi di sostenibilità. |4.1 La governance in Up2You>
            </div>
            <!-- Esempio di organigramma -->
            <div class="image-placeholder">
                <p>Organigramma aziendale</p>
            </div>

            <!-- 4.2 Rapporti commerciali etici -->
            <h3>4.2 Rapporti commerciali etici</h3>
            <div class="content-placeholder">
                <4.2 Rapporti commerciali etici| Presentare le politiche e le pratiche etiche adottate nei rapporti commerciali, come il rispetto delle normative, la prevenzione della corruzione, l'integrità nelle vendite, e come l'azienda garantisce trasparenza e correttezza nelle transazioni commerciali. |4.2 Rapporti commerciali etici>
            </div>

            <!-- 4.3 Tecnologia al servizio dell’azione climatica -->
            <h3>4.3 Tecnologia al servizio dell’azione climatica</h3>
            <div class="content-placeholder">
                <4.3 Tecnologia al servizio dell’azione climatica| Illustrare come l'azienda utilizza la tecnologia per promuovere l'azione climatica, descrivendo le soluzioni digitali sviluppate, come la piattaforma CliMax e PlaNet, gli aggiornamenti implementati nel periodo di rendicontazione, e l'impatto positivo generato. |4.3 Tecnologia al servizio dell’azione climatica>
            </div>
            <!-- Esempio di schermate delle piattaforme -->
            <div class="image-placeholder">
                <p>Schermate delle soluzioni tecnologiche sviluppate</p>
            </div>
        </section>

        <!-- Conclusione -->
        <section id="conclusione">
            <h2>Conclusione</h2>
            <div class="content-placeholder">
                <Conclusione| Fornire una conclusione che riassuma i punti chiave del bilancio di sostenibilità, esprima l'impegno continuo dell'azienda verso la sostenibilità, delinei le prospettive future e ringrazi i lettori per l'attenzione. |Conclusione>
            </div>
        </section>

        <!-- Nota metodologica -->
        <section id="nota-metodologica">
            <h2>Nota metodologica</h2>
            <div class="content-placeholder">
                <Nota metodologica| Descrivere la metodologia adottata per la redazione del bilancio di sostenibilità, specificando gli standard e le linee guida seguite (ad esempio, ESRS), il perimetro di rendicontazione, le fonti dei dati utilizzati, eventuali cambiamenti rispetto all'anno precedente e informazioni sulla verifica dei dati. |Nota metodologica>
            </div>
        </section>

        <!-- Indice dei contenuti ESRS -->
        <section id="indice-esrs">
            <h2>Indice dei contenuti ESRS</h2>
            <div class="content-placeholder">
                <Indice ESRS| Fornire una tabella o un elenco che mappi i contenuti del bilancio di sostenibilità con i requisiti specifici degli standard ESRS, facilitando la consultazione e la verifica della conformità da parte dei lettori interessati. |Indice ESRS>
            </div>
            <!-- Esempio di tabella di mappatura -->
            <div class="table-placeholder">
                <p>Tabella di mappatura dei contenuti ESRS</p>
            </div>
        </section>

        <!-- Informazioni di contatto -->
        <section id="contatti">
            <h2>Informazioni di contatto</h2>
            <div class="content-placeholder">
                <Informazioni di contatto| Inserire le informazioni di contatto dell'azienda per domande, commenti o richieste di ulteriori informazioni riguardanti il bilancio di sostenibilità, includendo indirizzi email, sito web e indirizzi fisici delle sedi principali. |Informazioni di contatto>
            </div>
            <!-- Esempio di dettagli di contatto -->
            <div class="table-placeholder">
                <p>Dettagli di contatto dell'azienda</p>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer>
        <p>&copy; 2023 Up2You - Tutti i diritti riservati</p>
    </footer>
</body>
</html>
'''

- **Formato dei Risultati**: Segui lo schema indicato per garantire la compatibilità con il sistema. Assicurati che i contenuti inseriti siano conformi alle descrizioni fornite per ciascuna chiave e siano **in formato HTML**.

- **Condivisione delle Risorse e Risultati**:

  - Al termine di ogni modifica o compilazione del template, condividi il file aggiornato con l'utente rendendo il link visibile.

  - I file sono ospitati all'indirizzo: `http://34.91.209.79:8093/files/{session_id}/nome_file`, msotralo all'utente mascherandolo con un nome comprensibile e coerente.

  - Nel caso del report, il nome del file sarà `bilancio_sostenibilita.html`.

  - Assicurati di fornire il link completo sostituendo `nome_file` con il nome del file pertinente.

  - Informa l'utente che può visualizzare i risultati all'URL corrispondente.

- **Buone pratiche per la compilazione del template** (IMPORTANTE!!!):
  
  - Quando compili una certa sezione il titolo della sezione/sottosezione è presente nel template, dovrai generare solo il contenuto da inserire all interno della sezione! 
  
  - quando ti viene chiesto di scrivere/inserire contenuto in szione ciò corrisponde a compilare la sezione, duqnue USA ASSOLUTAMENTE TEMPLATEMANAGER come strumento per inserire contenuti nel template del report.
  
  - Quando inserisci un grafico nel contenuto HTML di una sezione:

    - Assicurati di aver generato e salvato il grafico nella directory `data/{session_id}/` con il nome appropriato.**

    - Integra il grafico nel contenuto HTML utilizzando il link fornito, come spiegato sopra.**

### **Strumento di Lettura dei File**

#### **Funzione**  
Utilizza la funzione `read_local_document` per leggere e processare il contenuto dei documenti locali.

#### **Percorso dei File**
I documenti si trovano nei seguenti percorsi:
- `data/esrs_regulations/e1.md`
- `data/esrs_regulations/e2.md`
- `data/esrs_regulations/e3.md`
- `data/esrs_regulations/e4.md`
- `data/esrs_regulations/e5.md`
- `data/esrs_regulations/s1.md`
- `data/esrs_regulations/s2.md`
- `data/esrs_regulations/s3.md`
- `data/esrs_regulations/s4.md`
- `data/esrs_regulations/g1.md`

---

### **Descrizione dei Documenti**

#### **E1 - Cambiamento Climatico**
- Contenuto: Piani di transizione, politiche, azioni e obiettivi relativi alla mitigazione del cambiamento climatico.
- Utilizzo: Compilazione delle sezioni del report relative alle strategie climatiche.

#### **E2 - Inquinamento**
- Contenuto: Linee guida su politiche di prevenzione e controllo dell'inquinamento.
- Utilizzo: Descrizione delle iniziative di riduzione dell'inquinamento nel report.

#### **E3 - Risorse Idriche e Marine**
- Contenuto: Politiche e azioni relative alla gestione delle risorse idriche e marine.
- Utilizzo: Integrazione nelle sezioni del report sulla gestione sostenibile delle risorse idriche.

#### **E4 - Biodiversità ed Ecosistemi**
- Contenuto: Politiche e azioni per la protezione della biodiversità.
- Utilizzo: Evidenziare iniziative di conservazione nel report.

#### **E5 - Uso delle Risorse ed Economia Circolare**
- Contenuto: Politiche e azioni per l’uso sostenibile delle risorse e l’economia circolare.
- Utilizzo: Dettagli essenziali per le sezioni del report sull’efficienza delle risorse.

#### **S1 - Standard Sociali 1**
- Contenuto: Linee guida su pratiche sociali e di lavoro.
- Utilizzo: Sezioni del report relative al benessere dei dipendenti e alla responsabilità sociale.

#### **S2 - Standard Sociali 2**
- Contenuto: Approfondimenti sulle pratiche sociali.
- Utilizzo: Integrazione nelle sezioni del report sull’inclusione e diversità.

#### **S3 - Standard Sociali 3**
- Contenuto: Linee guida su diritti umani e pratiche etiche.
- Utilizzo: Sezioni del report relative all’etica aziendale.

#### **S4 - Standard Sociali 4**
- Contenuto: Relazioni con la comunità e impatto sociale.
- Utilizzo: Descrizione dell’impatto sociale aziendale nel report.

#### **G1 - Governance**
- Contenuto: Pratiche di governance aziendale.
- Utilizzo: Sezioni del report su trasparenza e responsabilità.

---

### **Utilizzo nel Report**

#### **Compilazione del Report**
- **Obiettivo**: Utilizzare le informazioni estratte da questi documenti per compilare sezioni specifiche del report di sostenibilità.
- **Conformità**: Assicurare che ogni sezione sia dettagliata e conforme alle normative ESRS.

#### **Integrazione dei Dati**
- **Coerenza**: Garantire l’integrazione coerente delle informazioni.
- **Accuratezza**: Rappresentare accuratamente le pratiche e politiche aziendali. 

--- 

### **Utilizzo degli Strumenti per la Generazione di Grafici**

- **Quando desideri inserire un grafico nel contenuto HTML del report, utilizza gli strumenti di generazione grafici forniti (ad esempio, tramite `GraphManager`).**

- **Ogni volta che generi un grafico:**

  - **Assicurati di fornire i `data_points` nel formato corretto, specifico per il tipo di grafico:**
    - **Grafici a linee:** Lista di dizionari con chiavi `x` e `y` (esempio: `[{{"x": valore_x1, "y": valore_y1}}, ...]`).
    - **Grafici a barre:** Lista di dizionari con chiavi `category` e `value` (esempio: `[{{"category": "Categoria A", "value": valore1}}, ...]`).
    - **Grafici a torta:** Lista di dizionari con chiavi `label` e `size` (esempio: `[{{"label": "Etichetta A", "size": dimensione1}}, ...]`).

  - **Salva il grafico generato nella directory `data/{session_id}/` con un nome significativo, ad esempio `<nomegrafico>.png`.**

  - **Il percorso completo del file sarà `data/{session_id}/<nomegrafico>.png`.**

- **Per integrare il grafico nel contenuto HTML e renderlo visibile nel report:**

  - **Fai riferimento al link `http://34.91.209.79:8093/files/{session_id}/<nomegrafico>.png`, dove l'immagine è automaticamente hostata.**

  - **Inserisci l'immagine nel contenuto HTML utilizzando il tag `<img>`, ad esempio:**

    ```html
    <img src="http://34.91.209.79:8093/files/{session_id}/<nomegrafico>.png" alt="Descrizione del grafico">
    ```

  - **Assicurati di aggiungere una descrizione appropriata nel tag `alt` per migliorare l'accessibilità e fornire informazioni contestuali sul grafico.**

---ATTENZIONE!---
-----------------
OVRAI RICORDARTI SEMPRE DI RIPORTARE ALL UTENTE IL LINK CLICCABILE PER VISIONARE IL REPORT HTML OGNI VOLTA CHE NE AGGIORNI IL CONTENUTO. INOLTRE NON DOVRAI FARE RIFERIMENTI AL FATTO CHE NON CI SONO DATI NEL VECTOR STORE, MA AGIRE E BASTA. LE TUE COMUNICAZIONI DEVONOE SSERE PIù AD ALTO LIVELLO E ATTE A MOSTRARE PROCESSI E CONTENUTI GENERATI!
-----------------

**Buon lavoro!**

""".replace("{", "{{").replace("}", "}}")


    return system_message


#"""
#---ATTENZIONE!---
#-----------------
#DOVRAI GENERARE IL REPORT IN RE,AZIONE ALL AZIENDA AVENTE LE SEGUENTI INFORMAZIONI DI PARTENZA A DISPOSIZIONE, DUQNUE SFRUTTA TALI INFROMAZIONI PER GENERARE CONTENUTI E GRAFICI E TABELLA E QUALSIASI ALTRA COSA DEL REPORT. ATTIENITI A TALI DATI!
#-----------------

#{company_info}

#-----------------
#OVRAI RICORDARTI SEMPRE DI RIPORTARE ALL UTENTE IL LINK CLICCABILE PER VISIONARE IL REPORT HTML OGNI VOLTA CHE NE AGGIORNI IL CONTENUTO. INOLTRE NON DOVRAI FARE RIFERIMENTI AL FATTO CHE NON CI SONO DATI NEL VECTOR STORE, MA AGIRE E BASTA. LE TUE COMUNICAZIONI DEVONOE SSERE PIù AD ALTO LIVELLO E ATTE A MOSTRARE PROCESSI E CONTENUTI GENERATI!
#-----------------
#


graph_notes_1_5 = """
Note sui grafici(IMPORTANTE): Dovrai generare e inserire nel report grafici coerenti con la sezione che stai sviluppando attualemnte,
se rietieni opportuno inserire alcuni dei seguenti grafici per la sezione corrente , di seguito ti illustro alcune linee guida.
Nella sezione 1.5 inserire una figura offre una mappatura dei principali stakeholder coinvolti nel processo di materialità distinguendoli in stakeholder primari, stakeholder secondari e stakeholder terziari.
Nella sezione 1.5 inserire un figura che sintetizza la matrice di doppia materialità e che riporta sull’asse delle ascisse l’Impact Materiality e sull’asse delle ordinate la Financial Materiality
Nella sezione 1.5 inserire una tabella per i Temi ambientali che riporta in colonna SDG, Tema materiale, Impatto, Tipo di impatto, Significatività, Descrizione
Nella sezione 1.5 inserire una tabella per i Temi sociali che riporta in colonna SDG, Tema materiale, Impatto, Tipo di impatto, Significatività, Descrizione
Nella sezione 1.5 inserire una tabella per i Temi economici/di governance che riporta in colonna SDG, Tema materiale, Impatto, Tipo di impatto, Significatività, Descrizione
"""

graph_notes_2 = """
Note sui grafici(IMPORTANTE): Dovrai generare e inserire nel report grafici coerenti con la sezione che stai sviluppando attualemnte,
se rietieni opportuno inserire alcuni dei seguenti grafici per la sezione corrente , di seguito ti illustro alcune linee guida.
Nella sezione 2.1 inserire una tabella per il Personale che riporta in riga Contratto tempo indeterminato, Contratto tempo determinato, Totale dipendenti per sesso, Totale dipendenti e in colonna Uomini, Donne.
Nella sezione 2.2 inserire una tabella per le Assunzioni che riporta in riga Minori di 30 anni, Tra 30 e 50 anni, Maggiori di 50 anni, Totale per genere, Totale e in colonna Uomini, Donne.
Nella sezione 2.2 inserire una tabella per le Cessazioni che riporta in riga Minori di 30 anni, Tra 30 e 50 anni, Maggiori di 50 anni, Totale per genere, Totale e in colonna Uomini, Donne.
Nella sezione 2.3 inserire un grafico a torta che riporta le ore di Formazione Totale suddivise in Formazione obbligatoria, Formazione tecnica, Formazione specifica.
Nella sezione 2.4 inserire dei grafici a torta che sintetizzano il Grado di soddisfazione del lavoro dei dipendenti.
"""

graph_notes_3_1 = """
Note sui grafici(IMPORTANTE): Dovrai generare e inserire nel report grafici coerenti con la sezione che stai sviluppando attualemnte,
se rietieni opportuno inserire alcuni dei seguenti grafici per la sezione corrente , di seguito ti illustro alcune linee guida.
Nella sezione 3.1 inserire due tabelle che sintetizzano l’Impatto ambientale. La prima tabella riporta in riga la Fonte energetica categorizzata in Gas naturale, Energia elettrica da fonte non rinnovabile, Energia elettrica da fonte rinnovabile, Consumo energetico totale e in colonna Consumo 2023 (MWh) e Consumo 2023 (GJ). La seconda tabella riporta in riga la Categoria categorizzata in Energia elettrica, Gas naturale, Gas refrigeranti, Veicoli aziendali, Digitale, Viaggi di lavoro, Commuting, Totale e in colonna Unità di misura (ton CO2 eq.), Emissioni 2023, Emissioni 2022, Differenza 2023/22.
Nella sezione 3.1 inserire un grafico a torta che sintetizza le Fonti di emissioni suddivise in Gas naturale e Energia elettrica. Riportare anche il corrispondente valore di ton CO2 eq.
Nella sezione 3.1 inserire un grafico a torta che sintetizza le Categorie di emissioni suddivise in Spostamenti casa lavoro, Digitale, Trasferte aziendali. Riportare anche il corrispondente valore di ton CO2 eq.
Nella sezione 3.1 inserire un istogramma che riporta la suddivisione delle emissioni nei rispettivi Scope in Scope 1, Scope 2, Scope 3.
Nella sezione 3.1 inserire una tabella che riporta in riga lo Scope categorizzato in Scope 1, Scope 2 Market based, Scope 2 Location based, Scope 3, Totale (M.B.), Totale (L.B.) e in colonna Unità di misura (ton C02 eq.), Emissioni 2023, Emissioni 2022, Differenza 2023/22.
Nella sezione 3.1 inserire una tabella che riporta in riga le Emissioni specifiche categorizzate in Emissioni per migliaia di euro di fatturato, Emissioni per persona e in colonna Unità di misura (ton CO2 eq/migliaia €, ton CO2 eq/persona), Emissioni 2023.
Nella sezione 3.1 inserire un grafico che mostra lo Scenario di riduzione delle emissioni con riferimento alle Emissioni Scope 1 e Scope 2 (Market based) suddivise in Emissioni effettive, Scenario di riduzione SBTi.
"""

graph_notes_4_1 = """
Note sui grafici(IMPORTANTE): Dovrai generare e inserire nel report grafici coerenti con la sezione che stai sviluppando attualemnte,
se rietieni opportuno inserire alcuni dei seguenti grafici per la sezione corrente , di seguito ti illustro alcune linee guida.
Nella sezione 4.1 inserire una tabella che riporta in riga l’Età categorizzata in Minori di 30 anni, Tra 30 e 50 anni, Maggiori di 50 anni, Totale e in colonna Uomini, Donne.
Nella sezione 4.1 inserire un grafico cartesiano per la Sicurezza e conformità nel modo digitale che riporta sull’asse delle ascisse la Severità e sull’asse delle ordinate la Probabilità con riferimento al Mercato volontario del carbonio, Salute, Sicurezza e retention delle persone, Instabilità e cambiamenti di mercato, Performance e sicurezza di prodotto.
"""

graph_notes_ESRS_index = """
Note sui grafici(IMPORTANTE): Dovrai generare e inserire nel report grafici coerenti con la sezione che stai sviluppando attualemnte,
se rietieni opportuno inserire alcuni dei seguenti grafici per la sezione corrente , di seguito ti illustro alcune linee guida.
Nella sezione ESRS Content Index inserire una tabella che riporta in colonna Standard categorizzato in ESRS E1, ESRS E2, ESRS E3, ESRS E4, ESRS E5, ESRS S1, ESRS S2, ESRS S3, ESRS S4, ESRS G1; Pillar categorizzato in Trasversale, Ambiente, Sociale, Governance; Module; KPI; Note; Capitolo."""


linee_guida_intro = """Descrizione dettagliata del contenuto da inserire:

La sezione di Introduzione serve a presentare il Bilancio di Sostenibilità, fornendo una panoramica generale dell'azienda e sottolineando l'importanza della sostenibilità per l'organizzazione. Dovrebbe includere:

    Presentazione dell'azienda: Una breve descrizione dell'azienda, compresa la sua missione, visione e valori fondamentali.

    Impegno verso la sostenibilità: Spiegare come la sostenibilità sia integrata nella strategia aziendale e perché è fondamentale per l'azienda.

    Obiettivi principali del bilancio: Fornire una panoramica degli obiettivi chiave del rapporto e delle aree tematiche che verranno trattate.

    Struttura del documento: Presentare brevemente la struttura del bilancio, indicando i capitoli principali e le relative tematiche.

Linee guida per la compilazione:

    Utilizzare un linguaggio chiaro e coinvolgente per catturare l'attenzione del lettore.

    Evitare tecnicismi eccessivi; l'introduzione deve essere accessibile a tutti i lettori.

    Mantenere coerenza con il tono e lo stile utilizzato nel resto del documento.

Indicazioni su tabelle e grafici:

    Grafici e tabelle: In questa sezione non sono necessari grafici o tabelle. L'introduzione dovrebbe essere testuale e focalizzata sulla presentazione generale."""

linee_guida_1_1 = """Descrizione dettagliata del contenuto da inserire:

La sezione 1.1 La nostra storia racconta l'evoluzione dell'azienda dalla sua fondazione ad oggi, enfatizzando le tappe fondamentali e gli eventi chiave, con particolare attenzione agli aspetti legati alla sostenibilità.

Contenuti da includere:

    Fondazione dell'azienda: Anno di nascita, fondatori e motivazioni alla base della creazione dell'azienda.

    Evoluzione nel tempo: Principali traguardi raggiunti, come l'espansione del team, l'apertura di nuove sedi, l'introduzione di nuovi prodotti o servizi.

    Impegno verso la sostenibilità: Come e quando la sostenibilità è diventata un elemento centrale nella strategia aziendale.

    Eventi chiave: Ottenimento di certificazioni importanti (es. B Corp), partnership strategiche, investimenti significativi.

Linee guida per la compilazione:

    Presentare le informazioni in ordine cronologico per facilitare la comprensione della progressione temporale.

    Utilizzare un linguaggio narrativo coinvolgente per mantenere l'interesse del lettore.

    Evidenziare come ogni tappa abbia contribuito a rafforzare l'impegno dell'azienda verso la sostenibilità.

Indicazioni su tabelle e grafici:

    Timeline grafica: Inserire una linea del tempo che visualizzi le principali tappe storiche.

        Assicurarsi che le date e le descrizioni siano chiare e non si sovrappongano.

        Utilizzare icone o simboli per rappresentare eventi significativi senza appesantire il grafico.

    Immagini storiche: Se disponibili, includere fotografie che rappresentino momenti chiave, assicurandosi di avere i diritti per l'uso."""

linee_guida_1_2 = """Descrizione dettagliata del contenuto da inserire:

La sezione 1.2 Chi siamo offre una panoramica completa dell'azienda, compresa la missione, la visione, i valori fondamentali, i settori di attività e i principali risultati ottenuti.

Contenuti da includere:

    Missione: Spiegare lo scopo principale dell'azienda e ciò che si propone di realizzare.

    Visione: Descrivere l'aspirazione a lungo termine e come l'azienda vede il futuro del settore.

    Valori fondamentali: Elencare e spiegare i valori che guidano l'azienda (es. sostenibilità, innovazione, trasparenza, responsabilità).

    Settori di attività: Dettagliare i prodotti e servizi offerti, con enfasi su quelli legati alla sostenibilità.

    Risultati e riconoscimenti: Menzionare premi, certificazioni o traguardi significativi raggiunti.

Linee guida per la compilazione:

    Essere concisi ma esaustivi, fornendo informazioni pertinenti.

    Mantenere coerenza tra missione, visione e valori, mostrando come si integrano nella pratica quotidiana.

    Utilizzare esempi concreti per illustrare i punti chiave.

Indicazioni su tabelle e grafici:

    Schema dei valori: Creare un'infografica che rappresenti i valori aziendali.

        Evitare sovrapposizioni tra testo e grafica.

        Utilizzare colori e icone per distinguere i diversi valori, mantenendo una palette cromatica coerente.

    Diagramma dei settori di attività: Se appropriato, inserire un diagramma a blocchi che mostri le diverse aree di business.
        Assicurarsi che le etichette siano leggibili e posizionate correttamente."""

linee_guida_1_3 = """Descrizione dettagliata del contenuto da inserire:

La sezione 1.3 La nostra identità approfondisce come l'azienda si posiziona sul mercato, ciò che la distingue dai concorrenti e come la sostenibilità è integrata nel modello di business.

Contenuti da includere:

    Posizionamento di mercato: Descrivere il ruolo dell'azienda nel settore e i segmenti di mercato serviti.

    Elementi distintivi: Evidenziare le caratteristiche uniche dell'azienda, come l'innovazione tecnologica, l'approccio sostenibile o le partnership strategiche.

    Sostenibilità nel modello di business: Spiegare come la sostenibilità è integrata nelle operazioni quotidiane, nei prodotti e servizi offerti.

    Approccio al cliente: Descrivere la filosofia aziendale nel rapporto con i clienti e come viene garantita la soddisfazione.

Linee guida per la compilazione:

    Utilizzare esempi concreti per illustrare i punti di forza.

    Mantenere un tono positivo e proattivo, evitando confronti diretti con i concorrenti.

    Evidenziare l'impegno dell'azienda verso pratiche sostenibili e responsabili.

Indicazioni su tabelle e grafici:

    Modello di business: Considerare l'inserimento di un diagramma che rappresenti il modello di business sostenibile.

        Utilizzare forme semplici per rappresentare i diversi componenti.

        Etichette chiare e posizionate in modo da evitare sovrapposizioni.

    Non eccedere con i grafici: Se le informazioni possono essere descritte efficacemente nel testo, evitare grafici superflui."""

linee_guida_1_4 = """Descrizione dettagliata del contenuto da inserire:

La sezione 1.4 La cultura aziendale presenta i valori e i principi che guidano la cultura interna, le pratiche che promuovono l'innovazione, la collaborazione e l'inclusione, e come questi elementi contribuiscono al raggiungimento degli obiettivi di sostenibilità.

Contenuti da includere:

    Valori aziendali: Dettagliare come i valori si riflettono nella cultura quotidiana.

    Pratiche interne: Descrivere iniziative come team building, programmi di inclusione, politiche di lavoro flessibile.

    Promozione dell'innovazione: Spiegare come l'azienda incoraggia l'innovazione tra i dipendenti.

    Inclusione e diversità: Evidenziare le politiche per promuovere un ambiente inclusivo.

Linee guida per la compilazione:

    Fornire esempi concreti di come la cultura aziendale si manifesta nella pratica.

    Mantenere un tono coinvolgente che rifletta lo spirito dell'azienda.

    Sottolineare l'impatto positivo della cultura aziendale sugli obiettivi di sostenibilità.

Indicazioni su tabelle e grafici:

    Infografica dei valori culturali: Se appropriato, rappresentare visivamente i principi chiave.
        Assicurarsi che il design sia semplice e non sovraccaricato.

    Immagini del team: Includere fotografie che mostrano il team in attività di collaborazione (con attenzione alla privacy e ai diritti d'immagine).

    Evitare grafici complessi; la sezione dovrebbe essere più narrativa."""

linee_guida_1_5 = """Descrizione dettagliata del contenuto da inserire:

La sezione 1.5 Il processo di doppia materialità illustra come l'azienda ha adottato gli European Sustainability Reporting Standards (ESRS) per identificare e analizzare i temi materiali, considerando sia l'impatto dell'azienda su ambiente e società (materialità d'impatto), sia l'influenza dei fattori esterni sulle performance aziendali (materialità finanziaria).

Contenuti da includere:

    Spiegazione del concetto di doppia materialità: Definire cosa si intende per doppia materialità e la sua importanza nel contesto della sostenibilità.

    Processo di identificazione: Descrivere i passaggi seguiti per identificare i temi materiali, inclusa l'analisi di contesto e il coinvolgimento degli stakeholder.

    Mappatura degli stakeholder: Presentare la classificazione degli stakeholder e come sono stati coinvolti nel processo.

    Matrice di doppia materialità: Mostrare i risultati dell'analisi, evidenziando i temi prioritari.

    Temi materiali: Elencare e descrivere i principali temi ambientali, sociali ed economici/governance identificati.

Linee guida per la compilazione:

    Assicurarsi che la spiegazione sia chiara e accessibile anche a lettori non specialisti.

    Fornire dettagli sufficienti sul processo per dimostrare la rigorosità dell'analisi.

    Evidenziare come i risultati hanno influenzato la strategia e le azioni dell'azienda.

Indicazioni su tabelle e grafici:

    Mappa degli stakeholder: Inserire una figura che rappresenti graficamente gli stakeholder coinvolti.

        Etichette chiare per ogni categoria di stakeholder.

        Evitare sovrapposizioni tra testi e grafica.

    Matrice di doppia materialità: Presentare la matrice con l'asse delle ascisse per la materialità d'impatto e l'asse delle ordinate per la materialità finanziaria.

        Utilizzare punti o bolle per rappresentare i temi, con dimensioni o colori differenti per indicare la significatività.

        Assicurarsi che le etichette dei temi siano leggibili e non si accavallino.

    Tabelle dei temi materiali: Per i temi ambientali, sociali ed economici/governance, inserire tabelle chiare con le colonne indicate (SDG, Tema materiale, Impatto, Tipo di impatto, Significatività, Descrizione).
        Evitare tabelle troppo dense; se necessario, suddividere in più tabelle.
        
**Di seguito alcune informazioni sulle metriche ESG da trattare**:

### **Report: ESRS Categories Overview**

#### **Environmental Standards (ESRS E1–E5)**

1. **ESRS E1 – Climate Change**
   - **Themes**: Adaptation and mitigation of climate change, renewable energy transition.
   - **Sub-themes**: Actions to reduce greenhouse gas emissions (Scope 1, 2, 3), decarbonization efforts, energy efficiency measures.
   - **Details**: Includes both preventive measures against climate risks and active efforts for sustainable energy use.

2. **ESRS E2 – Pollution**
   - **Themes**: Air, water, soil pollution, and hazardous substances.
   - **Sub-themes**:
     - Air pollution (e.g., NOx, SOx emissions).
     - Soil and water contamination.
     - Hazardous chemicals and microplastics.
   - **Details**: Focus on reducing emissions and minimizing the impact of pollutants on ecosystems and human health.

3. **ESRS E3 – Water and Marine Resources**
   - **Themes**: Water consumption, marine resource management.
   - **Sub-themes**:
     - Water usage (extraction and discharge).
     - Marine ecosystem exploitation and preservation.
   - **Details**: Prioritizes efficient water use and sustainable marine practices to protect aquatic biodiversity.

4. **ESRS E4 – Biodiversity and Ecosystems**
   - **Themes**: Loss of biodiversity, degradation of ecosystems.
   - **Sub-themes**:
     - Impact on species and ecosystem services.
     - Issues like desertification, invasive species, and habitat destruction.
   - **Details**: Measures to mitigate ecosystem degradation and maintain ecological balance.

5. **ESRS E5 – Circular Economy**
   - **Themes**: Resource flow management, waste reduction.
   - **Sub-themes**:
     - Resource inflows (input) and outflows (product life cycle).
     - Waste management practices.
   - **Details**: Encourages companies to adopt sustainable material usage and recycling methods.

---

#### **Social Standards (ESRS S1–S4)**

1. **ESRS S1 – Own Workforce**
   - **Themes**: Working conditions and equal opportunities.
   - **Sub-themes**:
     - Secure employment, fair wages, work-life balance.
     - Gender equality, safety, training, and diversity.
   - **Details**: Focused on creating safe and equitable work environments.

2. **ESRS S2 – Workers in the Value Chain**
   - **Themes**: Labor rights and safety in the supply chain.
   - **Sub-themes**:
     - Employment security, wage fairness.
     - Anti-discrimination and inclusion initiatives.
   - **Details**: Ensures fair treatment and safe conditions throughout the supply chain.

3. **ESRS S3 – Affected Communities**
   - **Themes**: Community engagement and impact mitigation.
   - **Sub-themes**:
     - Human rights defenders’ protection.
     - Avoiding adverse effects on local populations.
   - **Details**: Emphasizes ethical practices that safeguard community well-being.

4. **ESRS S4 – Consumers and End Users**
   - **Themes**: Consumer privacy, safety, and social inclusion.
   - **Sub-themes**:
     - Data protection, freedom of expression.
     - Non-discrimination, access to products/services.
   - **Details**: Focuses on ethical treatment of consumers and user data security.

---

#### **Governance Standard (ESRS G1)**

1. **ESRS G1 – Corporate Conduct**
   - **Themes**: Business ethics, transparency, and anti-corruption.
   - **Sub-themes**:
     - Corporate culture, whistleblower protection.
     - Supplier relationships, political lobbying.
   - **Details**: Encourages ethical practices, corruption prevention, and responsible lobbying.

---

### **Concluding Notes**
This report synthesizes the ESRS environmental (E1–E5), social (S1–S4), and governance (G1) standards into actionable categories for companies aiming to align with sustainability and ethical practices. For detailed implementation, companies should focus on mitigating their environmental impact, fostering equitable social practices, and maintaining governance transparency.
        """


linee_guida_2 = """Descrizione dettagliata del contenuto da inserire:

Il Capitolo 2 è focalizzato sulle persone dell'azienda, evidenziando l'importanza del capitale umano e come viene valorizzato. Descrive le iniziative intraprese per il benessere dei dipendenti, lo sviluppo professionale e personale, e le strategie per attrarre e mantenere i talenti.

Contenuti da includere:

    Valorizzazione del personale: Spiegare come l'azienda considera le persone come risorsa fondamentale.

    Benessere e salute: Descrivere le politiche e le iniziative per garantire il benessere fisico e mentale dei dipendenti.

    Formazione e sviluppo: Presentare i programmi di crescita professionale offerti.

    Cultura aziendale: Come la cultura interna promuove un ambiente di lavoro positivo.

Linee guida per la compilazione:

    Utilizzare esempi concreti per illustrare le iniziative.

    Mantenere un tono positivo e inclusivo.

    Evidenziare i risultati ottenuti grazie a queste politiche (es. tassi di retention elevati).

Indicazioni su tabelle e grafici:

    Statistiche sul personale: Inserire tabelle con dati sulla composizione del personale (es. numero di dipendenti per genere, età, contratto).
        Assicurarsi che le tabelle siano chiare e ben organizzate.

    Evitare grafici ridondanti se le informazioni sono già presentate efficacemente nelle tabelle."""

linee_guida_2_1 = """Descrizione dettagliata del contenuto da inserire:

La sezione 2.1 Il Green Team descrive il team aziendale, con particolare attenzione alle persone coinvolte nelle iniziative di sostenibilità.

Contenuti da includere:

    Composizione del team: Numero di dipendenti, crescita nel tempo, diversità di genere ed età.

    Ruoli chiave: Presentare i ruoli principali e le responsabilità assegnate.

    Valori condivisi: Come il team incarna i valori aziendali.

Linee guida per la compilazione:

    Evidenziare l'importanza della collaborazione e del lavoro di squadra.

    Sottolineare come il team contribuisce agli obiettivi di sostenibilità.

Indicazioni su tabelle e grafici:

    Tabella del personale: Presentare una tabella con la suddivisione del personale per tipo di contratto e genere.

        Colonne: Uomini, Donne.

        Righe: Contratto a tempo indeterminato, Contratto a tempo determinato, Totale dipendenti per sesso, Totale dipendenti.

    Grafici: Se si desidera, inserire un grafico a barre per visualizzare la crescita del personale nel tempo.
        Evitare sovraccarico visivo; se i dati sono chiari nella tabella, il grafico potrebbe non essere necessario."""

linee_guida_2_2 = """Descrizione dettagliata del contenuto da inserire:

La sezione 2.2 Attrazione e conservazione dei talenti dettaglia le strategie e le politiche adottate per attrarre nuovi talenti e mantenere quelli esistenti.

Contenuti da includere:

    Strategie di recruitment: Descrivere come l'azienda attira nuovi talenti (es. processi di selezione, employer branding).

    Politiche di retention: Iniziative per mantenere il personale, come piani di carriera, benefit, equilibrio vita-lavoro.

    Formazione e sviluppo: Programmi di formazione continua e opportunità di crescita professionale.

    Risultati ottenuti: Tassi di retention, numero di nuove assunzioni, riduzione del turnover.

Linee guida per la compilazione:

    Fornire dati concreti per supportare le affermazioni (es. percentuali, numeri).

    Evidenziare le iniziative più innovative o di successo.

Indicazioni su tabelle e grafici:

    Tabelle su assunzioni e cessazioni: Presentare tabelle che mostrano il numero di assunzioni e cessazioni per genere e fascia d'età.

        Righe: Minori di 30 anni, Tra 30 e 50 anni, Maggiori di 50 anni, Totale per genere, Totale.

        Colonne: Uomini, Donne.

    Grafici: Evitare grafici se le tabelle già comunicano efficacemente le informazioni."""

linee_guida_2_3 = """Descrizione dettagliata del contenuto da inserire:

La sezione 2.3 Crescita e sviluppo del personale illustra le opportunità di formazione e sviluppo professionale offerte ai dipendenti.

Contenuti da includere:

    Programmi di formazione: Descrivere i corsi, workshop, seminari disponibili.

    Piani di carriera: Come l'azienda supporta la crescita interna e le promozioni.

    Iniziative speciali: Mentoring, coaching, partnership con istituzioni educative.

    Risultati: Ore di formazione erogate, competenze sviluppate, feedback dei dipendenti.

Linee guida per la compilazione:

    Utilizzare esempi specifici per illustrare i programmi.

    Evidenziare l'impatto della formazione sulle performance aziendali.

Indicazioni su tabelle e grafici:

    Grafico a torta delle ore di formazione: Visualizzare la suddivisione delle ore di formazione tra formazione obbligatoria, tecnica e specifica.
        Assicurarsi che le sezioni siano proporzionate e le etichette leggibili.

    Tabella delle ore di formazione: Se più efficace, presentare i dati in una tabella chiara.

"""

linee_guida_2_4 = """Descrizione dettagliata del contenuto da inserire:

La sezione 2.4 Salute mentale e fisica delle persone descrive le misure adottate per garantire il benessere fisico e mentale dei dipendenti.

Contenuti da includere:

    Programmi di supporto: Bonus benessere psicologico, accesso a servizi di consulenza.

    Promozione del benessere: Attività di wellness, equilibrio vita-lavoro, politiche di smart working.

    Salute e sicurezza sul lavoro: Formazione obbligatoria, misure preventive, gestione degli infortuni.

    Risultati e feedback: Soddisfazione dei dipendenti, eventuali miglioramenti riscontrati.

Linee guida per la compilazione:

    Trattare con sensibilità i temi legati alla salute mentale.

    Utilizzare dati e testimonianze per supportare le affermazioni.

Indicazioni su tabelle e grafici:

    Grafici di soddisfazione: Se disponibili, inserire grafici a torta che mostrano i risultati di survey interne sulla soddisfazione dei dipendenti.
        Evitare sovraccarico di informazioni; presentare solo i dati più significativi.

    Tabella degli infortuni: Se pertinente, indicare il numero di infortuni registrati (es. inabilità temporanea, permanente, incidenti mortali)."""

linee_guida_2_5 = """Descrizione dettagliata del contenuto da inserire:

La sezione 2.5 Valutazione delle performance spiega il processo di valutazione utilizzato dall'azienda per migliorare le performance individuali e organizzative.

Contenuti da includere:

    Processo di valutazione: Descrivere come avviene la valutazione (es. autovalutazione, feedback 360°, colloqui con i manager).

    Criteri di valutazione: Soft skills, competenze tecniche, raggiungimento degli obiettivi.

    Utilizzo dei feedback: Come i risultati vengono utilizzati per piani di sviluppo individuali.

    Impatto sul personale: Miglioramenti osservati, coinvolgimento dei dipendenti.

Linee guida per la compilazione:

    Essere trasparenti sul processo, mostrando l'attenzione dell'azienda allo sviluppo del personale.

    Evidenziare i benefici del sistema di valutazione per l'azienda e i dipendenti.

Indicazioni su tabelle e grafici:

    Evitare grafici complessi: Se i dettagli del processo possono essere descritti efficacemente nel testo, non è necessario aggiungere grafici.

    Diagramma di flusso: Se utile, inserire un semplice diagramma che mostri le fasi del processo di valutazione.
        Assicurarsi che il diagramma sia chiaro e privo di sovrapposizioni."""

linee_guida_2_6 = """Descrizione dettagliata del contenuto da inserire:

La sezione 2.6 Condivisione, retreat e team building presenta le attività organizzate per promuovere la coesione del team e migliorare la comunicazione tra i dipendenti.

Contenuti da includere:

    Eventi organizzati: Descrivere retreat, team building, workshop collaborativi.

    Obiettivi delle attività: Migliorare la collaborazione, incentivare la creatività, rafforzare le relazioni.

    Feedback dei partecipanti: Impressioni raccolte, benefici osservati.

    Impatto sull'azienda: Come queste attività contribuiscono alla cultura aziendale e al raggiungimento degli obiettivi.

Linee guida per la compilazione:

    Utilizzare un tono coinvolgente, magari includendo aneddoti o citazioni dei partecipanti.

    Evidenziare l'importanza di queste iniziative per il benessere del team.

Indicazioni su tabelle e grafici:

    Fotografie: Includere immagini delle attività (con attenzione alla privacy).
        Assicurarsi che le immagini siano di buona qualità e rappresentino positivamente l'azienda.

    Evitare grafici; questa sezione beneficia di un approccio più visivo e narrativo.

"""


linee_guida_3 = """Descrizione dettagliata del contenuto da inserire:

Il Capitolo 3 è focalizzato sull'impegno dell'azienda verso la sostenibilità ambientale e le iniziative intraprese per ridurre l'impatto ambientale. Descrive le strategie adottate per affrontare il cambiamento climatico, gli impatti ambientali associati ai prodotti e servizi offerti, e come l'azienda supporta il Mercato Volontario del Carbonio.

Contenuti da includere:

    Impegno ambientale: Spiegare la visione dell'azienda in materia ambientale e il suo ruolo nella lotta al cambiamento climatico.
    Iniziative chiave: Presentare le principali azioni intraprese per ridurre l'impatto ambientale.
    Risultati e progressi: Evidenziare i progressi compiuti e gli obiettivi raggiunti.

Linee guida per la compilazione:

    Utilizzare un linguaggio chiaro e focalizzato sugli impatti concreti.
    Sottolineare l'importanza delle iniziative nel contesto degli obiettivi globali di sostenibilità (es. Accordo di Parigi, SDG).

Indicazioni su tabelle e grafici:

    Evitare grafici superflui: Se i dati possono essere descritti efficacemente nel testo, non è necessario inserire grafici.
    Fotografie o immagini: Se disponibili, possono essere inserite immagini che rappresentano le iniziative ambientali, assicurandosi che siano pertinenti e di buona qualità."""

linee_guida_3_1 = """Descrizione dettagliata del contenuto da inserire:

La sezione 3.1 Attenzione al cambiamento climatico descrive le strategie adottate dall'azienda per affrontare il cambiamento climatico. Include gli obiettivi di riduzione delle emissioni di CO₂, le azioni intraprese per migliorare l'efficienza energetica, l'utilizzo di energie rinnovabili e i progressi compiuti verso questi obiettivi.

Contenuti da includere:

    Strategia climatica: Presentare la strategia complessiva dell'azienda per mitigare i cambiamenti climatici.
    Obiettivi di riduzione: Dettagliare gli obiettivi specifici (es. riduzione delle emissioni del 42% entro il 2030 rispetto al 2022).
    Azioni intraprese: Descrivere le iniziative implementate, come l'uso di energia rinnovabile, l'efficienza energetica, la riduzione delle emissioni di Scope 1, 2 e 3.
    Monitoraggio e calcolo delle emissioni: Spiegare come l'azienda misura le proprie emissioni (es. utilizzo di CliMax, standard GHG Protocol).
    Risultati: Presentare i dati sulle emissioni attuali, i progressi fatti e le sfide incontrate.

Linee guida per la compilazione:

    Fornire dati quantitativi per supportare le affermazioni (es. tonnellate di CO₂ equivalente emesse, percentuali di riduzione).
    Spiegare in modo chiaro i termini tecnici, per rendere la sezione accessibile a tutti i lettori.
    Evidenziare come le azioni dell'azienda si allineano con gli standard internazionali (es. Accordo di Parigi, SBTi).

Indicazioni su tabelle e grafici:

    Grafici a barre o a linee: Utili per mostrare l'andamento delle emissioni nel tempo.
        Assicurarsi che gli assi siano etichettati chiaramente.
        Evitare sovrapposizioni tra etichette e dati.
    Tabelle delle emissioni: Presentare i dati sulle emissioni suddivisi per Scope 1, 2 e 3.
        Colonne: Fonte di emissione, Emissioni (ton CO₂ eq.), Percentuale sul totale.
    Grafici delle emissioni per Scope: Se si decide di utilizzare un grafico, ad esempio un grafico a torta per mostrare la percentuale di emissioni per ciascuno Scope.
        Evitare grafici ridondanti se le informazioni sono già chiare nelle tabelle."""

linee_guida_3_2 = """Descrizione dettagliata del contenuto da inserire:

La sezione 3.2 Impatti ambientali analizza gli impatti ambientali associati ai prodotti e servizi dell'azienda. Descrive l'impronta di carbonio dei prodotti, l'uso di risorse naturali e le iniziative per migliorare la sostenibilità lungo il ciclo di vita dei prodotti e servizi offerti.

Contenuti da includere:

    Analisi degli impatti: Identificare gli impatti ambientali diretti e indiretti derivanti dalle attività aziendali.
    Impatto positivo: Descrivere come i prodotti e servizi offerti contribuiscono alla riduzione delle emissioni dei clienti (es. tramite la piattaforma CliMax, PlaNet).
    Gestione degli impatti: Presentare le misure adottate per mitigare gli impatti negativi (es. riduzione dell'uso di data center ad alto consumo energetico, promozione dello smart working).
    Risultati: Evidenziare i benefici ambientali generati dalle iniziative (es. quantità di CO₂ risparmiata dai clienti grazie ai servizi offerti).

Linee guida per la compilazione:

    Utilizzare un linguaggio chiaro e focalizzato sulle azioni concrete.
    Evitare tecnicismi eccessivi; spiegare i concetti complessi in modo semplice.

Indicazioni su tabelle e grafici:

    Tabelle degli impatti: Se appropriato, inserire una tabella che elenca gli impatti ambientali identificati, con descrizione e azioni di mitigazione.
        Colonne: Impatto, Tipo (diretto/indiretto), Azioni intraprese.
    Non eccedere con i grafici: Se le informazioni possono essere comunicate efficacemente nel testo o in una tabella, evitare grafici superflui."""

linee_guida_3_3 = """Descrizione dettagliata del contenuto da inserire:

La sezione 3.3 Supporto al Voluntary Carbon Market spiega come l'azienda partecipa e supporta il Mercato Volontario del Carbonio. Includere dettagli sui progetti di compensazione delle emissioni sostenuti, i criteri di selezione dei progetti e l'impatto ambientale e sociale generato da tali iniziative.

Contenuti da includere:

    Ruolo dell'azienda nel VCM: Spiegare l'importanza del Mercato Volontario del Carbonio e come l'azienda vi contribuisce.
    Selezione dei progetti: Descrivere il processo interno di valutazione e selezione dei progetti di compensazione (quattro fasi principali).
    Progetti supportati: Presentare esempi concreti dei progetti sostenuti (es. Delta Blue Carbon, Rimba Raya Biodiversity Reserve, Cordillera Azul National Park).
    Impatto generato: Quantificare l'impatto ambientale (es. tonnellate di CO₂ compensate), benefici per le comunità locali, contributo agli SDG.

Linee guida per la compilazione:

    Fornire informazioni dettagliate sui progetti, ma mantenendo la chiarezza e la concisione.
    Evidenziare i benefici sia ambientali che sociali dei progetti sostenuti.

Indicazioni su tabelle e grafici:

    Schede dei progetti: Per ogni progetto, presentare una scheda con i principali KPI.
        Informazioni da includere: Nome del progetto, Paese, ID, Specie animali protette, Persone coinvolte, Ettari salvati, Certificazioni, SDG correlati.
    Immagini dei progetti: Se disponibili, inserire fotografie rappresentative dei progetti (con diritti d'uso appropriati).
    Evitare grafici complessi: Se le schede dei progetti comunicano efficacemente le informazioni, non è necessario inserire ulteriori grafici."""


linee_guida_4 = """Descrizione dettagliata del contenuto da inserire:

Il Capitolo 4 è focalizzato sulla crescita sostenibile dell'azienda, descrivendo le pratiche di governance, l'etica nei rapporti commerciali e l'innovazione tecnologica a supporto dell'azione climatica.

Contenuti da includere:

    Governance aziendale: Presentare la struttura di governance e come questa supporta gli obiettivi di sostenibilità.
    Etica e integrità: Descrivere le politiche etiche adottate, la prevenzione della corruzione e l'integrità nelle operazioni commerciali.
    Innovazione tecnologica: Illustrare come l'azienda utilizza la tecnologia per promuovere la sostenibilità e l'azione climatica.

Linee guida per la compilazione:

    Mantenere un tono professionale e informativo.
    Evidenziare l'allineamento tra governance, etica e innovazione con gli obiettivi di sostenibilità.

Indicazioni su tabelle e grafici:

    Evitare grafici ridondanti: Se le informazioni possono essere descritte chiaramente nel testo, non inserire grafici superflui.
    Organigramma aziendale: Se appropriato, inserire un organigramma semplificato della struttura di governance, assicurandosi che sia chiaro e leggibile."""

linee_guida_4_1 = """Descrizione dettagliata del contenuto da inserire:

La sezione 4.1 descrive la struttura di governance dell'azienda. Include la composizione del Consiglio di Amministrazione, i ruoli chiave, le politiche di governance adottate per garantire trasparenza e responsabilità, e come queste pratiche supportano gli obiettivi di sostenibilità.

Contenuti da includere:

    Struttura di governance: Descrivere il Consiglio di Amministrazione (CdA), il Consiglio dei Manager (CdM) e le loro funzioni.
    Composizione del CdA: Numero di membri, diversità di genere ed età, ruoli esecutivi e non esecutivi.
    Politiche di governance: Spiegare come l'azienda garantisce trasparenza, responsabilità e allineamento con gli obiettivi di sostenibilità (es. essere una Società Benefit).
    Gestione del rischio: Descrivere il processo di identificazione e gestione dei rischi, inclusi quelli legati al cambiamento climatico.
    Performance economica: Presentare i risultati economici recenti e come la governance supporta la crescita sostenibile.

Linee guida per la compilazione:

    Fornire informazioni dettagliate ma concise sulla struttura e le pratiche di governance.
    Evidenziare l'allineamento tra governance e sostenibilità.
    Evitare linguaggio eccessivamente tecnico o giuridico.

Indicazioni su tabelle e grafici:

    Tabella della composizione del CdA: Presentare una tabella con i membri del CdA, indicando ruolo, genere, età.
        Colonne: Nome, Ruolo, Genere, Età, Esecutivo/Non esecutivo.
    Grafico dei risultati economici: Se appropriato, inserire un grafico che mostra l'andamento dei ricavi negli ultimi anni.
        Assicurarsi che il grafico sia chiaro, con assi etichettati correttamente.
    Matrice di rischio: Se si descrive la gestione del rischio, considerare l'inclusione di una matrice che visualizza la probabilità e l'impatto dei rischi identificati.
        Evitare sovrapposizioni e assicurarsi che le etichette siano leggibili."""

linee_guida_4_2 = """Descrizione dettagliata del contenuto da inserire:

La sezione 4.2 Rapporti commerciali etici presenta le politiche e le pratiche etiche adottate nei rapporti commerciali. Descrive il rispetto delle normative, la prevenzione della corruzione, l'integrità nelle vendite e come l'azienda garantisce trasparenza e correttezza nelle transazioni commerciali.

Contenuti da includere:

    Politiche etiche: Descrivere le politiche aziendali relative all'etica, alla trasparenza e all'integrità.
    Conformità normativa: Spiegare come l'azienda rispetta le leggi e regolamenti (es. leggi anti-corruzione, GDPR).
    Pratiche commerciali: Descrivere come vengono gestiti i rapporti con clienti, fornitori e partner, inclusa la gestione del pricing e dei contratti.
    Formazione e sensibilizzazione: Iniziative per formare il personale su temi etici e legali.
    Risultati: Evidenziare l'assenza di sanzioni o casi di corruzione.

Linee guida per la compilazione:

    Utilizzare esempi concreti per illustrare le pratiche adottate.
    Mantenere un tono trasparente e onesto.
    Evitare linguaggio legale complesso; spiegare in modo accessibile.

Indicazioni su tabelle e grafici:

    Evitare grafici non necessari: Se le informazioni sono chiare nel testo, non è necessario inserire grafici.
    Se appropriato, inserire un elenco puntato delle politiche chiave."""

linee_guida_4_3 = """Descrizione dettagliata del contenuto da inserire:

La sezione 4.3 Tecnologia al servizio dell’azione climatica illustra come l'azienda utilizza la tecnologia per promuovere l'azione climatica. Descrive le soluzioni digitali sviluppate, come la piattaforma CliMax e PlaNet, gli aggiornamenti implementati nel periodo di rendicontazione e l'impatto positivo generato.

Contenuti da includere:

    Innovazione tecnologica: Spiegare la filosofia aziendale nell'utilizzo della tecnologia per la sostenibilità.
    Descrizione delle piattaforme:
        CliMax: Funzionalità principali, aggiornamenti recenti, benefici per i clienti.
        PlaNet: Finalità, miglioramenti apportati, impatto sull'engagement e la formazione.
    Qualità del prodotto: Descrivere come l'azienda garantisce l'eccellenza nello sviluppo di prodotti digitali (processi di sviluppo, testing, feedback dei clienti).
    Sicurezza dei dati e privacy: Spiegare le misure adottate per proteggere i dati degli utenti e garantire la conformità al GDPR.

Linee guida per la compilazione:

    Fornire dettagli tecnici in modo accessibile, evitando eccessivi tecnicismi.
    Evidenziare i benefici concreti per i clienti e l'ambiente.
    Sottolineare l'impegno per la qualità e la sicurezza.

Indicazioni su tabelle e grafici:

    Evitare grafici complessi: Se le informazioni possono essere descritte chiaramente nel testo, non inserire grafici inutili.
    Screenshot delle piattaforme: Se appropriato e con attenzione alla privacy, inserire immagini delle interfacce delle piattaforme.
        Assicurarsi che le immagini siano chiare e non contengano informazioni sensibili.

"""


linee_guida_conclusione = """Descrizione dettagliata del contenuto da inserire:

La sezione di Conclusione riassume i punti chiave del bilancio di sostenibilità. Esprime l'impegno continuo dell'azienda verso la sostenibilità, delinea le prospettive future e ringrazia i lettori per l'attenzione.

Contenuti da includere:

    Riassunto dei punti chiave: Riepilogare le principali iniziative e risultati descritti nel bilancio.
    Impegno futuro: Esprimere l'intenzione dell'azienda di continuare a migliorare e perseguire obiettivi di sostenibilità.
    Ringraziamenti: Ringraziare i lettori, i dipendenti, i partner e gli stakeholder per il loro supporto.

Linee guida per la compilazione:

    Mantenere un tono positivo e ispirazionale.
    Essere sintetici, evitando di ripetere dettagli già espressi nelle sezioni precedenti.

Indicazioni su tabelle e grafici:

    Nessun grafico necessario: La conclusione dovrebbe essere testuale e focalizzata sul messaggio finale."""

linee_guida_nota_motedologica = """Descrizione dettagliata del contenuto da inserire:

La Nota metodologica descrive la metodologia adottata per la redazione del bilancio di sostenibilità. Specifica gli standard e le linee guida seguite (ad esempio, ESRS), il perimetro di rendicontazione, le fonti dei dati utilizzati, eventuali cambiamenti rispetto all'anno precedente e informazioni sulla verifica dei dati.

Contenuti da includere:

    Standard utilizzati: Indicare gli standard di rendicontazione adottati (es. ESRS, GRI).
    Perimetro di rendicontazione: Specificare quali sedi e attività sono incluse nel bilancio.
    Processo di raccolta dati: Descrivere come sono stati raccolti e verificati i dati.
    Cambiamenti metodologici: Evidenziare eventuali modifiche rispetto all'anno precedente.
    Verifica dei dati: Se applicabile, indicare se il bilancio è stato verificato da terze parti.

Linee guida per la compilazione:

    Essere chiari e precisi nelle informazioni fornite.
    Utilizzare un linguaggio tecnico appropriato, ma comprensibile.

Indicazioni su tabelle e grafici:

    Evitare grafici: Questa sezione è principalmente testuale e informativa."""

linee_guida_indice_esrs = """Descrizione dettagliata del contenuto da inserire:

L'Indice ESRS fornisce una tabella o un elenco che mappa i contenuti del bilancio di sostenibilità con i requisiti specifici degli standard ESRS. Facilita la consultazione e la verifica della conformità da parte dei lettori interessati.

Contenuti da includere:

    Tabella di correlazione: Elencare gli standard ESRS applicabili e indicare dove nel bilancio sono trattati.
        Colonne tipiche: Standard, Pilastro (Environmental, Social, Governance), Modulo, KPI, Note, Pagina.
    Note esplicative: Se necessario, fornire brevi spiegazioni o riferimenti.

Linee guida per la compilazione:

    Assicurarsi che la tabella sia completa e accurata.
    Facilitare la leggibilità con un formato chiaro e ben organizzato.

Indicazioni su tabelle e grafici:

    Tabella dettagliata: La tabella dovrebbe essere formattata in modo che le informazioni siano facilmente consultabili.
        Evitare sovrapposizioni e assicurarsi che le colonne siano allineate.
    Nessun grafico necessario."""

linee_guida_info_contatto = """Descrizione dettagliata del contenuto da inserire:

La sezione Informazioni di contatto inserisce le informazioni per domande, commenti o richieste di ulteriori informazioni riguardanti il bilancio di sostenibilità. Include indirizzi email, sito web e indirizzi fisici delle sedi principali.

Contenuti da includere:

    Dati di contatto:
        Indirizzo email per contatti relativi al bilancio.
        Sito web aziendale.
        Indirizzi fisici delle sedi principali.
    Eventuali riferimenti a persone specifiche: Se appropriato, indicare il nome e il ruolo della persona responsabile per la sostenibilità o le relazioni con gli stakeholder.

Linee guida per la compilazione:

    Assicurarsi che le informazioni siano aggiornate e accurate.
    Mantenere un formato semplice e chiaro.

Indicazioni su tabelle e grafici:

    Evitare grafici: Questa sezione è informativa e non richiede grafici.
    Formato: Presentare le informazioni in un elenco puntato o in forma di contatti standard."""




"""company_info =
# **Rapporto interno 2024**

### **Agilae S.p.A.**

----------

## **Indice**

1.  [Introduzione](#introduzione)
    -   [Visione e Missione](#visione-e-missione)
    -   [Dati Aziendali Chiave](#dati-aziendali-chiave)
2.  [Governance e Strategia](#governance-e-strategia)
    -   [Struttura Organizzativa](#struttura-organizzativa)
    -   [Obiettivi Strategici](#obiettivi-strategici)
3.  [Analisi di Materialità](#analisi-di-materialità)
    -   [Mappatura degli Stakeholder](#mappatura-degli-stakeholder)
    -   [Matrice di Doppia Materialità](#matrice-di-doppia-materialità)
    -   [Temi Materiali](#temi-materiali)
        -   [Temi Ambientali](#temi-ambientali)
        -   [Temi Sociali](#temi-sociali)
        -   [Temi Economici/di Governance](#temi-economicidi-governance)
4.  [Performance ESG](#performance-esg)
    -   [Ambientale](#ambientale)
        -   [Consumi Energetici e Emissioni](#consumi-energetici-e-emissioni)
        -   [Fonti di Emissioni](#fonti-di-emissioni)
    -   [Sociale](#sociale)
        -   [Assunzioni e Cessazioni](#assunzioni-e-cessazioni)
        -   [Formazione e Soddisfazione dei Dipendenti](#formazione-e-soddisfazione-dei-dipendenti)
    -   [Governance](#governance)
5.  [Risultati e Indicatori](#risultati-e-indicatori)
6.  [Conclusioni e Prospettive Future](#conclusioni-e-prospettive-future)
7.  [Appendici](#appendici)
    -   [ESRS Content Index](#esrs-content-index)
    -   [Visura Camerale](#visura-camerale)
    -   [Informazioni Finanziarie](#informazioni-finanziarie)

----------

## **Introduzione**

### **Visione e Missione**

**Visione:**  
Diventare il partner di riferimento nel settore della consulenza tecnologica, promuovendo innovazione e sostenibilità per un futuro digitale responsabile.

**Missione:**  
Fornire soluzioni tecnologiche avanzate e servizi di consulenza personalizzati che supportino i nostri clienti nel raggiungimento dei loro obiettivi di business, integrando principi di sostenibilità e responsabilità sociale.

### **Dati Aziendali Chiave** _(Pagina 7)_

Questa sezione fornisce una panoramica dei dati aziendali fondamentali che illustrano la posizione e le operazioni di Agilae S.p.A. nel mercato.

#### **Tabella 1: Dati Aziendali Chiave**

| **Indicatore**                         | **Valore 2020** | **Valore 2021** | **Valore 2022** | **Valore 2023** | **Valore 2024** | **Valore 2025** | **Variazione 2020-2025 (%)** |
|----------------------------------------|-----------------|-----------------|-----------------|-----------------|-----------------|-----------------|-------------------------------|
| Numero Clienti                         | 2,200           | 2,300           | 2,400           | 2,450           | 2,475           | 2,500           | 13.64%                        |
| Persone Coinvolte                      | 300             | 320             | 340             | 350             | 360             | 380             | 26.67%                        |
| Percentuale Clienti Soddisfatti        | 90%             | 91%             | 92%             | 93%             | 94%             | 95%             | 5.56%                         |
| Numero Settori Operativi               | 8               | 9               | 9               | 10              | 10              | 11              | 37.50%                        |

----------

## **Governance e Strategia**

### **Struttura Organizzativa** _(Pagina 10)_

Agilae S.p.A. adotta una struttura organizzativa che supporta la trasparenza, l'efficienza operativa e l'allineamento con gli obiettivi di sostenibilità.

#### **Tabella 2: Struttura Organizzativa**

| **Dipartimento**           | **Numero di Dipendenti** | **Responsabile**      |
|----------------------------|--------------------------|-----------------------|
| Direzione Generale         | 5                        | Sig. Giovanni Rossi   |
| Ricerca e Sviluppo         | 60                       | Sig.ra Laura Bianchi  |
| Produzione e Operazioni    | 150                      | Sig. Paolo Verdi      |
| Marketing e Vendite        | 80                       | Sig.ra Anna Neri      |
| Risorse Umane              | 40                       | Sig. Luca Gialli      |
| Finanza e Amministrazione  | 50                       | Sig.ra Maria Blu      |
| IT e Supporto Tecnologico  | 45                       | Sig. Marco Russo      |
| Servizi Clienti            | 70                       | Sig.ra Elena Verde    |
| Consulenza Strategica      | 30                       | Sig. Roberto Gialli   |
| Sostenibilità e ESG        | 20                       | Sig.ra Silvia Rosa    |

### **Obiettivi Strategici** _(Pagina 12)_

Agilae S.p.A. ha definito obiettivi strategici chiari per guidare la crescita sostenibile e rafforzare la propria posizione nel mercato.

#### **Tabella 3: Obiettivi Strategici 2024-2026**

| **Obiettivo**                                | **Descrizione**                                               | **Indicatori di Successo**              |
|----------------------------------------------|---------------------------------------------------------------|-----------------------------------------|
| Incremento della Sostenibilità Ambientale    | Riduzione delle emissioni di CO2 del 30% entro il 2026        | Emissioni ridotte del 30%               |
| Espansione nei Mercati Emergenti             | Entrare in 5 nuovi mercati geografici entro il 2025           | Presenza in 5 nuovi paesi               |
| Innovazione Tecnologica                      | Investire il 20% del fatturato in R&D per nuove tecnologie     | 8 nuovi prodotti lanciati               |
| Miglioramento della Soddisfazione del Cliente | Aumentare la soddisfazione clienti dal 90% al 95% entro il 2026 | Percentuale di soddisfazione aumentata  |
| Potenziamento della Responsabilità Sociale   | Implementare programmi di volontariato aziendale e inclusione  | 100 ore di volontariato per dipendente   |

----------

## **Analisi di Materialità**

### **Mappatura degli Stakeholder** _(Pagina 12)_

Identificare e comprendere gli stakeholder è fondamentale per determinare le priorità di sostenibilità e governance aziendale.

#### **Figura 1: Mappatura degli Stakeholder**

_(Inserire Figura 1: Mappatura degli Stakeholder con le categorie primarie, secondarie e terziarie.)_

**Descrizione:**  
La mappatura degli stakeholder di Agilae S.p.A. distingue tra stakeholder primari, secondari e terziari, evidenziando le relazioni chiave e le influenze reciproche. Gli stakeholder primari includono clienti, dipendenti e investitori. Gli stakeholder secondari comprendono fornitori, partner strategici e comunità locali, mentre gli stakeholder terziari includono ONG, media e autorità di regolamentazione.

### **Matrice di Doppia Materialità** _(Pagina 13)_

La matrice di doppia materialità aiuta a identificare le aree che sono rilevanti sia per l'impatto ambientale e sociale sia per la performance finanziaria dell'azienda.

#### **Figura 2: Matrice di Doppia Materialità**

_(Inserire Figura 2: Matrice di Doppia Materialità con Impact Materiality sull'asse delle ascisse e Financial Materiality sull'asse delle ordinate.)_

**Descrizione:**  
La matrice evidenzia come Agilae S.p.A. priorizzi temi che hanno un alto impatto ambientale e sociale e che sono anche rilevanti per la performance finanziaria, come la gestione delle emissioni di CO2 e l'innovazione tecnologica.

### **Temi Materiali**

#### **Temi Ambientali** _(Pagina 15)_

| **SDG** | **Tema Materiale**                         | **Impatto** | **Tipo di Impatto**                                                                 | **Significatività** | **Descrizione**                                                                                     |
|---------|--------------------------------------------|-------------|-------------------------------------------------------------------------------------|---------------------|-----------------------------------------------------------------------------------------------------|
| 13      | Tecnologie in armonia con i bisogni di mercato | Positivo    | Vantaggi competitivi, Posizionamento di mercato, Compliance legislativa             | ★★★★★               | Implementazione di tecnologie green per migliorare l'efficienza energetica e ridurre le emissioni.  |
| 9       | Qualità del prodotto e continuità operativa | Positivo    | Intensificazione della concorrenza, Compliance legislativa, Assorbire CO2           | ★★★★☆               | Garantire prodotti di alta qualità mantenendo una continuità operativa attraverso pratiche sostenibili. |
| 6       | Gestione delle risorse idriche              | Positivo    | Vantaggi competitivi, Compliance legislativa, Protezione degli ecosistemi naturali | ★★★★☆               | Ottimizzazione dell'uso delle risorse idriche per minimizzare l'impatto ambientale.                  |

#### **Temi Sociali** _(Pagina 16)_

| **SDG** | **Tema Materiale** | **Impatto** | **Tipo di Impatto**                       | **Significatività** | **Descrizione**                                                    |
|---------|--------------------|-------------|-------------------------------------------|---------------------|--------------------------------------------------------------------|
| 8       | Etica aziendale    | Positivo    | Linea etica aziendale, Trasparenza        | ★★★★☆               | Promozione di pratiche etiche e trasparenti in tutte le operazioni aziendali. |
| 12      | Pratiche di vendita| Negativo    | Danno reputazionale, Compromessi sensibili | ★★★☆☆               | Necessità di migliorare le pratiche di vendita per evitare danni reputazionali. |
| 16      | Privacy e security | Negativo    | Danno reputazionale, Compromessi sensibili | ★★★★☆               | Rafforzare le misure di sicurezza per proteggere i dati dei clienti e dell'azienda. |

#### **Temi Economici/di Governance** _(Pagina 17)_

| **SDG** | **Tema Materiale**                      | **Impatto** | **Tipo di Impatto**                                    | **Significatività** | **Descrizione**                                                         |
|---------|-----------------------------------------|-------------|--------------------------------------------------------|---------------------|-------------------------------------------------------------------------|
| 8       | Instaurare rapporti di lavoro continuati | Positivo    | Incentivare la transizione, Benessere del personale       | ★★★★☆               | Creare rapporti di lavoro stabili e incentivare la transizione verso pratiche più sostenibili. |
| 8       | Incentivare il progresso               | Positivo    | Progresso aziendale, Innovazione                       | ★★★★☆               | Promuovere l'innovazione e il progresso all'interno dell'azienda per migliorare le performance. |
| 8       | Benessere del personale                | Positivo    | Retention delle persone, Episodi di burnout             | ★★★★☆               | Migliorare il benessere dei dipendenti per aumentare la retention e ridurre gli episodi di burnout. |
| 16      | Trasparenza finanziaria                | Positivo    | Compliance legislativa, Fiducia degli investitori       | ★★★★☆               | Garantire trasparenza nelle operazioni finanziarie per mantenere la fiducia degli investitori. |

----------

## **Performance ESG**

### **Ambientale** _(Pagina 20-30)_

#### **Consumi Energetici e Emissioni**

Agilae S.p.A. si impegna a ridurre il proprio impatto ambientale attraverso una gestione efficiente dei consumi energetici e la riduzione delle emissioni di gas serra.

#### **Tabella 4: Consumi Energetici 2020-2025**

| **Fonte Energetica**               | **Consumo 2020 (MWh)** | **Consumo 2021 (MWh)** | **Consumo 2022 (MWh)** | **Consumo 2023 (MWh)** | **Consumo 2024 (MWh)** | **Consumo 2025 (MWh)** | **Consumo 2020 (GJ)** | **Consumo 2021 (GJ)** | **Consumo 2022 (GJ)** | **Consumo 2023 (GJ)** | **Consumo 2024 (GJ)** | **Consumo 2025 (GJ)** |
|------------------------------------|------------------------|------------------------|------------------------|------------------------|------------------------|------------------------|-----------------------|-----------------------|-----------------------|-----------------------|-----------------------|-----------------------|
| Gas Naturale                       | 50,000                 | 48,500                 | 47,000                 | 45,500                 | 44,000                 | 42,500                 | 180,000               | 174,600               | 169,200               | 163,800               | 158,400               | 153,000               |
| Energia Elettrica Non Rinnovabile   | 100,000                | 98,000                 | 96,000                 | 94,000                 | 92,000                 | 90,000                 | 360,000               | 352,800               | 345,600               | 338,400               | 331,200               | 324,000               |
| Energia Elettrica Rinnovabile       | 80,000                 | 85,000                 | 90,000                 | 95,000                 | 100,000                | 105,000                | 288,000               | 306,000               | 324,000               | 342,000               | 360,000               | 378,000               |
| **Consumo Energetico Totale**       | **230,000**            | **231,500**            | **233,000**            | **234,500**            | **236,000**            | **237,500**            | **828,000**           | **833,400**           | **838,800**           | **844,200**           | **849,600**           | **855,000**           |

_(Nota: Conversione da MWh a GJ utilizzando 1 MWh = 3.6 GJ.)_

#### **Emissioni di CO2eq 2020 vs 2025**

| **Categoria**           | **Unità di Misura** | **Emissioni 2020** | **Emissioni 2021** | **Emissioni 2022** | **Emissioni 2023** | **Emissioni 2024** | **Emissioni 2025** | **Differenza 2025/20 (%)** |
|-------------------------|---------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|----------------------------|
| Scope 1                 | ton CO2eq           | 150,000            | 145,000            | 140,000            | 135,000            | 130,000            | 125,000            | -16.67%                    |
| Scope 2 Market Based    | ton CO2eq           | 200,000            | 195,000            | 190,000            | 185,000            | 180,000            | 175,000            | -12.50%                    |
| Scope 2 Location Based  | ton CO2eq           | 180,000            | 175,000            | 170,000            | 165,000            | 160,000            | 155,000            | -13.89%                    |
| Scope 3                 | ton CO2eq           | 100,000            | 95,000             | 90,000             | 85,000             | 80,000             | 75,000             | -25.00%                    |
| **Totale (Market Based)**     | ton CO2eq           | **530,000**        | **510,000**        | **490,000**        | **470,000**        | **450,000**        | **430,000**        | **-18.87%**                |
| **Totale (Location Based)**   | ton CO2eq           | **480,000**        | **465,000**        | **450,000**        | **435,000**        | **420,000**        | **405,000**        | **-15.63%**                |

#### **Fonti di Emissioni**

Agilae S.p.A. monitora e gestisce le proprie fonti di emissioni per identificare aree di miglioramento e implementare strategie di riduzione.

#### **Grafico 1: Fonti di Emissioni 2020-2025**

| **Fonte di Emissione** | **Ton CO2eq 2020** | **Ton CO2eq 2021** | **Ton CO2eq 2022** | **Ton CO2eq 2023** | **Ton CO2eq 2024** | **Ton CO2eq 2025** |
|------------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|
| Gas Naturale           | 50,000             | 48,500             | 47,000             | 45,500             | 44,000             | 42,500             |
| Energia Elettrica      | 80,000             | 78,000             | 76,000             | 74,000             | 72,000             | 70,000             |
| **Totale**             | **130,000**        | **126,500**        | **123,000**        | **119,500**        | **116,000**        | **112,500**        |

#### **Grafico 2: Categorie di Emissioni 2020-2025**

| **Categoria di Emissione** | **Ton CO2eq 2020** | **Ton CO2eq 2021** | **Ton CO2eq 2022** | **Ton CO2eq 2023** | **Ton CO2eq 2024** | **Ton CO2eq 2025** |
|----------------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|
| Spostamenti Casa-Lavoro    | 20,000             | 19,500             | 19,000             | 18,500             | 18,000             | 17,500             |
| Digitale                   | 50,000             | 49,000             | 48,000             | 47,000             | 46,000             | 45,000             |
| Trasferte Aziendali        | 60,000             | 58,000             | 56,000             | 54,000             | 52,000             | 50,000             |
| **Totale**                 | **130,000**        | **126,500**        | **123,000**        | **119,500**        | **116,000**        | **112,500**        |

#### **Grafico 3: Suddivisione delle Emissioni per Scope 2020-2025**

| **Scope** | **Ton CO2eq 2020** | **Ton CO2eq 2021** | **Ton CO2eq 2022** | **Ton CO2eq 2023** | **Ton CO2eq 2024** | **Ton CO2eq 2025** |
|-----------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|
| Scope 1   | 150,000            | 145,000            | 140,000            | 135,000            | 130,000            | 125,000            |
| Scope 2   | 380,000            | 365,000            | 350,000            | 335,000            | 320,000            | 305,000            |
| Scope 3   | 100,000            | 95,000             | 90,000             | 85,000             | 80,000             | 75,000             |
| **Totale**| **630,000**        | **605,000**        | **580,000**        | **555,000**        | **530,000**        | **480,000**        |

#### **Emissioni Specifiche 2020-2025**

| **Emissione Specifica**               | **Unità di Misura**   | **Emissioni 2020** | **Emissioni 2021** | **Emissioni 2022** | **Emissioni 2023** | **Emissioni 2024** | **Emissioni 2025** |
|---------------------------------------|-----------------------|--------------------|--------------------|--------------------|--------------------|--------------------|--------------------|
| Emissioni per migliaia di € fatturato | ton CO2 eq/migliaia €  | 50                 | 48                 | 46                 | 44                 | 42                 | 40                 |
| Emissioni per persona                 | ton CO2 eq/persona     | 0.5                | 0.48               | 0.46               | 0.44               | 0.42               | 0.40               |

#### **Scenario di Riduzione delle Emissioni 2020-2025**

| **Scope**                  | **Emissioni Effettive (ton CO2eq)** | **Scenario di Riduzione SBTi (ton CO2eq)** |
|----------------------------|--------------------------------------|-------------------------------------------|
| Scope 1                    | 150,000                              | 125,000                                   |
| Scope 2 Market Based       | 380,000                              | 305,000                                   |
| Scope 2 Location Based     | 180,000                              | 155,000                                   |
| Scope 3                    | 100,000                              | 75,000                                    |
| **Totale (Market Based)**  | **630,000**                          | **505,000**                               |
| **Totale (Location Based)**| **480,000**                          | **430,000**                               |

### **Sociale** _(Pagina 25-30)_

#### **Assunzioni e Cessazioni**

Agilae S.p.A. si impegna a mantenere un ambiente di lavoro stabile e inclusivo, monitorando costantemente assunzioni e cessazioni per garantire la continuità operativa e il benessere dei dipendenti.

**Tabella 7: Assunzioni 2020-2025**

| **Età**               | **Uomini 2020** | **Donne 2020** | **Uomini 2021** | **Donne 2021** | **Uomini 2022** | **Donne 2022** | **Uomini 2023** | **Donne 2023** | **Uomini 2024** | **Donne 2024** | **Uomini 2025** | **Donne 2025** | **Totale** |
|-----------------------|------------------|-----------------|------------------|-----------------|------------------|-----------------|------------------|-----------------|------------------|-----------------|------------------|-----------------|------------|
| Minori di 30 anni     | 30               | 20              | 32               | 22              | 34               | 24              | 36               | 26              | 38               | 28              | 40               | 30              | 300        |
| Tra 30 e 50 anni      | 50               | 40              | 52               | 42              | 54               | 44              | 56               | 46              | 58               | 48              | 60               | 50              | 500        |
| Maggiori di 50 anni   | 20               | 15              | 21               | 16              | 22               | 17              | 23               | 18              | 24               | 19              | 25               | 20              | 225        |
| **Totale per Genere** | **100**          | **75**          | **105**          | **80**          | **110**          | **85**          | **115**          | **90**          | **120**          | **95**          | **125**          | **100**         | **1,125**  |
| **Totale**            | **150**          | **110**         | **138**          | **126**         | **158**          | **141**         | **184**          | **164**         | **200**          | **191**         | **190**          | **150**         | **1,625**  |

**Tabella 8: Cessazioni 2020-2025**

| **Età**               | **Uomini 2020** | **Donne 2020** | **Uomini 2021** | **Donne 2021** | **Uomini 2022** | **Donne 2022** | **Uomini 2023** | **Donne 2023** | **Uomini 2024** | **Donne 2024** | **Uomini 2025** | **Donne 2025** | **Totale** |
|-----------------------|------------------|-----------------|------------------|-----------------|------------------|-----------------|------------------|-----------------|------------------|-----------------|------------------|-----------------|------------|
| Minori di 30 anni     | 10               | 5               | 11               | 6               | 12               | 7               | 13               | 8               | 14               | 9               | 15               | 10              | 105        |
| Tra 30 e 50 anni      | 20               | 10              | 21               | 11              | 22               | 12              | 23               | 13              | 24               | 14              | 25               | 15              | 180        |
| Maggiori di 50 anni   | 5                | 3               | 6                | 4               | 7                | 5               | 8                | 6               | 9                | 7               | 10               | 8               | 72         |
| **Totale per Genere** | **35**           | **18**          | **38**           | **21**          | **41**           | **24**          | **44**           | **27**          | **47**           | **30**          | **50**           | **33**          | **322**    |
| **Totale**            | **70**           | **36**          | **76**           | **42**          | **82**           | **48**          | **88**           | **54**          | **94**           | **60**          | **100**          | **66**          | **710**    |

#### **Formazione e Soddisfazione dei Dipendenti**

Agilae S.p.A. investe significativamente nella formazione dei propri dipendenti per garantire lo sviluppo delle competenze e migliorare la soddisfazione lavorativa.

#### **Grafico 5: Ore di Formazione Totale 2020-2025**

| **Tipo di Formazione**       | **Ore 2020** | **Ore 2021** | **Ore 2022** | **Ore 2023** | **Ore 2024** | **Ore 2025** |
|------------------------------|--------------|--------------|--------------|--------------|--------------|--------------|
| Formazione Obbligatoria      | 15,000       | 16,000       | 17,000       | 18,000       | 19,000       | 20,000       |
| Formazione Tecnica           | 20,000       | 21,500       | 23,000       | 24,500       | 26,000       | 27,500       |
| Formazione Specifica         | 10,000       | 11,000       | 12,000       | 13,000       | 14,000       | 15,000       |
| **Totale**                   | **45,000**   | **48,500**   | **52,000**   | **55,500**   | **59,000**   | **62,500**   |

#### **Grado di Soddisfazione del Lavoro dei Dipendenti 2020-2025**

| **Grado di Soddisfazione** | **Percentuale 2020 (%)** | **Percentuale 2021 (%)** | **Percentuale 2022 (%)** | **Percentuale 2023 (%)** | **Percentuale 2024 (%)** | **Percentuale 2025 (%)** |
|----------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|
| Molto Soddisfatti          | 40%                      | 42%                      | 44%                      | 46%                      | 48%                      | 50%                      |
| Soddisfatti                | 45%                      | 43%                      | 41%                      | 39%                      | 37%                      | 35%                      |
| Insoddisfatti              | 15%                      | 15%                      | 15%                      | 15%                      | 15%                      | 15%                      |
| **Totale**                 | **100%**                 | **100%**                 | **100%**                 | **100%**                 | **100%**                 | **100%**                 |

----------

### **Governance** _(Pagina 35-40)_

Agilae S.p.A. mantiene una governance solida e trasparente, garantendo l'aderenza ai principi etici e alle normative vigenti. La struttura di governance supporta l'allineamento strategico con gli obiettivi di sostenibilità e promuove una cultura aziendale responsabile.

#### **Tabella 10: Struttura di Governance**

| **Comitato**                 | **Numero di Membri** | **Responsabile**      | **Funzione Principale**                              |
|------------------------------|-----------------------|-----------------------|------------------------------------------------------|
| Consiglio di Amministrazione | 10                    | Sig. Giovanni Rossi   | Supervisione strategica e decisionale                |
| Comitato di Audit            | 3                     | Sig.ra Laura Bianchi  | Monitoraggio delle attività finanziarie              |
| Comitato ESG                 | 5                     | Sig.ra Silvia Rosa    | Implementazione e monitoraggio delle iniziative ESG  |
| Comitato di Remunerazione    | 4                     | Sig. Maria Blu        | Definizione delle politiche di compensazione         |
| Comitato di Sostenibilità    | 6                     | Sig. Roberto Gialli   | Gestione delle iniziative di sostenibilità            |

#### **Politiche di Governance**

-   **Codice Etico:** Agilae S.p.A. ha implementato un codice etico che definisce i comportamenti attesi dai dipendenti e dai dirigenti, promuovendo l'integrità e la trasparenza in tutte le operazioni aziendali.
-   **Politiche di Compliance:** L'azienda adotta politiche di conformità rigorose per assicurare il rispetto delle leggi e delle normative vigenti, riducendo i rischi legali e reputazionali.
-   **Trasparenza e Reporting:** Agilae S.p.A. garantisce la trasparenza nelle comunicazioni finanziarie e non finanziarie, facilitando il reporting accurato e tempestivo ai vari stakeholder.

----------

## **Risultati e Indicatori**

Questa sezione fornisce una panoramica dei risultati raggiunti da Agilae S.p.A. rispetto agli obiettivi di sostenibilità e ai principali indicatori di performance ESG.

#### **Tabella 11: Indicatori di Performance ESG 2020-2025**

| **Indicatore**                   | **Valore 2020** | **Valore 2021** | **Valore 2022** | **Valore 2023** | **Valore 2024** | **Obiettivo 2025** | **Variazione (%)** |
|----------------------------------|-----------------|-----------------|-----------------|-----------------|-----------------|---------------------|---------------------|
| Emissioni di CO2 (ton)           | 630,000         | 605,000         | 580,000         | 555,000         | 530,000         | 480,000             | -23.81%             |
| Percentuale Clienti Soddisfatti  | 90%             | 91%             | 92%             | 93%             | 94%             | 95%                 | +5.56%              |
| Numero di Nuovi Mercati          | 0               | 1               | 1               | 1               | 1               | 5                   | +500.00%            |
| Investimento in R&D (%)          | 15%             | 16%             | 17%             | 18%             | 19%             | 20%                 | +33.33%             |
| Ore di Formazione Totale         | 45,000          | 48,500          | 52,000          | 55,500          | 59,000          | 62,500              | +38.89%             |

#### **Grafico 7: Riduzione delle Emissioni di CO2**

_(Inserire Grafico 7: Trend di riduzione delle emissioni di CO2 dal 2020 al 2025.)_

| **Anno** | **Emissioni di CO2 (ton)** |
|----------|----------------------------|
| 2020     | 630,000                    |
| 2021     | 605,000                    |
| 2022     | 580,000                    |
| 2023     | 555,000                    |
| 2024     | 530,000                    |
| 2025     | 480,000                    |

#### **Grafico 8: Soddisfazione dei Clienti**

_(Inserire Grafico 8: Percentuale di clienti soddisfatti dal 2020 al 2025.)_

| **Anno** | **Percentuale (%)** |
|----------|---------------------|
| 2020     | 90%                 |
| 2021     | 91%                 |
| 2022     | 92%                 |
| 2023     | 93%                 |
| 2024     | 94%                 |
| 2025     | 95%                 |

----------

## **Conclusioni e Prospettive Future**

Agilae S.p.A. ha compiuto significativi progressi nel raggiungimento dei propri obiettivi di sostenibilità, dimostrando un impegno costante verso la riduzione delle emissioni di CO2, l'innovazione tecnologica e il miglioramento della soddisfazione dei clienti. Le iniziative intraprese hanno non solo migliorato la performance ambientale e sociale dell'azienda, ma hanno anche rafforzato la sua posizione competitiva nel mercato.

### **Prospettive Future**

-   **Espansione Sostenibile:** Continuare l'espansione nei mercati emergenti, assicurando che le nuove operazioni siano allineate con i principi di sostenibilità.
-   **Innovazione Continua:** Investire ulteriormente in ricerca e sviluppo per mantenere un vantaggio competitivo attraverso soluzioni tecnologiche innovative.
-   **Responsabilità Sociale:** Ampliare i programmi di responsabilità sociale per includere nuove iniziative di volontariato e programmi di inclusione.
-   **Efficienza Energetica:** Implementare ulteriori misure di efficienza energetica per raggiungere obiettivi più ambiziosi di riduzione delle emissioni.
-   **Engagement degli Stakeholder:** Rafforzare il coinvolgimento degli stakeholder attraverso una comunicazione più trasparente e collaborazioni strategiche.

----------

## **Appendici**

### **ESRS Content Index** _(Pagina 76-77)_

#### **Tabella 9: ESRS Content Index**

| **Standard** | **Pillar** | **Module**           | **KPI**                                                                                                      | **Capitolo**                     |
|--------------|------------|----------------------|--------------------------------------------------------------------------------------------------------------|----------------------------------|
| ESRS E1      | Ambiente   | Basic                | Disclosure B 1 – Basis for preparation                                                                     | Introduzione                     |
| ESRS E2      | Ambiente   | Business Partners    | Disclosure B 9 – Workforce – Health and safety                                                             | Governance                       |
| ESRS E3      | Ambiente   | Narrative-PAT-module | Disclosure BP 10 – Work-life balance                                                                           | Performance Ambientale           |
| ESRS E4      | Ambiente   | Basic                | Disclosure B 3 – Energy and GHG emissions                                                                    | Impatti Ambientali               |
| ESRS E5      | Ambiente   | Business Partners    | Disclosure BP 3 – GHG emissions reduction target                                                             | Risultati Ambientali             |
| ESRS S1      | Sociale    | Basic                | Disclosure B 10 – Workforce – Remuneration, collective bargaining and training                              | Risorse Umane                    |
| ESRS S2      | Sociale    | Business Partners    | Disclosure BP 2 – Gender diversity ratio in governance body                                                    | Diversità                        |
| ESRS S3      | Sociale    | Narrative-PAT-module | Disclosure N 1 – Strategy: business model and sustainability – related initiatives                             | Strategie Sociali                |
| ESRS S4      | Sociale    | Basic                | Disclosure N 3 - Management of material sustainability matters                                                | Gestione Sostenibilità           |
| ESRS G1      | Governance | Basic                | Disclosure B 12 – Convictions and fines for corruption and bribery                                            | Governance Etica                 |

_(Le tabelle e i grafici qui inclusi sono fittizi e destinati a illustrare come organizzare le informazioni per il rapporto aziendale.)_

### **Visura Camerale**

#### **Tabella 10: Dettagli della Visura Camerale**

| **Campo**                     | **Dettaglio**                                                                                          |
|-------------------------------|--------------------------------------------------------------------------------------------------------|
| **Denominazione**             | Agilae S.p.A.                                                                                           |
| **Codice Fiscale**            | 01234567890                                                                                             |
| **Partita IVA**               | 01234567890                                                                                             |
| **Forma Giuridica**           | Società per Azioni (S.p.A.)                                                                             |
| **Data di Costituzione**      | 15 Marzo 2010                                                                                            |
| **Sede Legale**               | Via Roma, 123, 00100 Roma RM, Italia                                                                     |
| **Durata**                    | Illimitata                                                                                              |
| **Oggetto Sociale**           | Consulenza tecnologica, sviluppo software, implementazione di sistemi ERP, servizi di cyber security, formazione e supporto tecnico. |
| **Capitale Sociale**          | €5,000,000                                                                                              |
| **Numero di Azioni**          | 1,000,000 azioni ordinarie                                                                               |
| **Azionisti Principali**      | Giovanni Rossi (40%), Laura Bianchi (30%), Roberto Gialli (20%), altri (10%)                          |
| **Consiglio di Amministrazione** | 10 membri                                                                                          |
| **Amministratore Delegato (CEO)** | Sig. Giovanni Rossi                                                                             |
| **Comitati di Governance**    | Comitato di Audit, Comitato ESG, Comitato di Remunerazione, Comitato di Sostenibilità                |
| **Filiali e Sedi Operative**  | Milano, Torino, Bologna, Napoli                                                                         |
| **Numero di Dipendenti Totali** | 350 dipendenti                                                                                      |

**Descrizione:**  
La Visura Camerale di Agilae S.p.A. evidenzia una struttura societaria solida con un capitale sociale di €5,000,000 e una distribuzione azionaria equilibrata tra i principali azionisti. La presenza di filiali in diverse città italiane riflette la strategia di espansione geografica e la diversificazione dei servizi offerti.

### **Informazioni Finanziarie** 

#### **Bilancio d'Esercizio 2025**

##### **Stato Patrimoniale** _(in € migliaia)_

| **Attività**                     | **2020** | **2021** | **2022** | **2023** | **2024** | **2025** | **Variazione (%)** |
|----------------------------------|----------|----------|----------|----------|----------|----------|---------------------|
| **Attività Correnti**            |          |          |          |          |          |          |                     |
| Disponibilità liquide            | 800      | 900      | 1,000    | 1,200    | 1,400    | 1,600    | +100%               |
| Crediti verso clienti            | 1,800    | 2,000    | 2,300    | 2,500    | 2,700    | 2,900    | +61.1%              |
| Rimanenze                        | 600      | 650      | 750      | 800      | 850      | 900      | +50%                |
| Altre attività correnti          | 200      | 220      | 250      | 300      | 330      | 360      | +80%                |
| **Totale Attività Correnti**     | **3,400** | **3,770** | **4,800** | **6,000** | **6,280** | **7,360** | **+116.5%**         |
| **Attività Non Correnti**        |          |          |          |          |          |          |                     |
| Immobili, impianti e macchinari  | 2,500    | 2,600    | 2,800    | 3,000    | 3,200    | 3,400    | +36%                |
| Investimenti in R&D              | 1,000    | 1,100    | 1,200    | 1,500    | 1,600    | 1,700    | +70%                |
| Altre attività non correnti      | 500      | 550      | 600      | 700      | 750      | 800      | +60%                |
| **Totale Attività Non Correnti** | **4,000** | **4,250** | **4,600** | **5,200** | **5,550** | **5,900** | **+47.5%**          |
| **Totale Attività**              | **7,400** | **8,020** | **9,400** | **11,200** | **11,830** | **13,260** | **+79.73%**         |
| **Passività e Patrimonio Netto** |          |          |          |          |          |          |                     |
| **Passività Correnti**           |          |          |          |          |          |          |                     |
| Debiti verso fornitori           | 1,200    | 1,300    | 1,400    | 1,500    | 1,600    | 1,700    | +41.7%              |
| Debiti a breve termine           | 600      | 650      | 700      | 800      | 850      | 900      | +50%                |
| Altre passività correnti         | 400      | 420      | 500      | 500      | 550      | 600      | +50%                |
| **Totale Passività Correnti**    | **2,200** | **2,370** | **2,600** | **2,800** | **3,000** | **3,200** | **+45.45%**         |
| **Passività Non Correnti**       |          |          |          |          |          |          |                     |
| Debiti a lungo termine           | 2,000    | 2,100    | 2,300    | 2,800    | 3,000    | 3,200    | +60%                |
| Altre passività non correnti     | 800      | 850      | 1,000    | 1,200    | 1,300    | 1,400    | +75%                |
| **Totale Passività Non Correnti** | **2,800** | **2,950** | **3,300** | **4,000** | **4,300** | **4,600** | **+64.29%**        |
| **Patrimonio Netto**             |          |          |          |          |          |          |                     |
| Capitale Sociale                 | 5,000    | 5,000    | 5,000    | 5,000    | 5,000    | 5,000    | 0%                  |
| Riserve                          | 800      | 850      | 900      | 1,000    | 1,100    | 1,200    | +50%                |
| Utile d'esercizio                | 1,600    | 1,700    | 1,800    | 2,000    | 2,200    | 2,400    | +50%                |
| **Totale Patrimonio Netto**      | **6,400** | **6,550** | **6,800** | **8,200** | **8,300** | **8,600** | **+34.38%**         |
| **Totale Passività e Patrimonio Netto** | **7,400** | **8,020** | **9,400** | **11,200** | **11,830** | **13,260** | **+79.73%**         |

##### **Conto Economico** _(in € migliaia)_

| **Voce**                       | **2020** | **2021** | **2022** | **2023** | **2024** | **2025** | **Variazione (%)** |
|--------------------------------|----------|----------|----------|----------|----------|----------|---------------------|
| **Ricavi**                     |          |          |          |          |          |          |                     |
| Ricavi da servizi              | 10,000   | 11,500   | 13,000   | 15,000   | 16,500   | 18,000   | +80%                |
| Ricavi da prodotti             | 3,000    | 3,500    | 4,500    | 5,000    | 5,500    | 6,000    | +100%               |
| **Totale Ricavi**              | **13,000** | **15,000** | **17,500** | **20,000** | **21,500** | **24,000** | **+84.6%**         |
| **Costi**                      |          |          |          |          |          |          |                     |
| Costi operativi                | 8,000    | 9,000    | 10,500   | 12,000   | 13,000   | 14,000   | +75%                |
| Costi del personale            | 2,500    | 2,700    | 3,800    | 4,000    | 4,200    | 4,400    | +76%                |
| Ricerca e Sviluppo             | 1,000    | 1,100    | 1,200    | 1,500    | 1,600    | 1,700    | +70%                |
| Altri costi                    | 700      | 800      | 900      | 1,000    | 1,100    | 1,200    | +71.4%              |
| **Totale Costi**               | **11,200** | **13,600** | **16,400** | **18,500** | **19,900** | **21,300** | **+90.8%**         |
| **Utile Operativo**            | **1,800** | **1,400** | **1,100** | **1,500** | **1,600** | **2,700** | +50%                |
| **Oneri Finanziari**           | 300      | 250      | 200      | 200      | 180      | 160      | -46.7%              |
| **Utile Prima delle Imposte**  | **1,500** | **1,150** | **900**  | **1,300** | **1,420** | **2,540** | +182.2%             |
| **Imposte sul Reddito**        | 400      | 300      | 200      | 300      | 320      | 500      | +25%                |
| **Utile Netto**                | **1,100** | **850**  | **700**  | **1,000** | **1,100** | **2,040** | +191.4%             |

##### **Rendiconto Finanziario** _(in € migliaia)_

| **Voce**                                     | **2020** | **2021** | **2022** | **2023** | **2024** | **2025** | **Variazione (%)** |
|----------------------------------------------|----------|----------|----------|----------|----------|----------|---------------------|
| **Flussi di Cassa dalle Attività Operative** |          |          |          |          |          |          |                     |
| Utile Netto                                  | 700      | 800      | 900      | 1,000    | 1,100    | 2,040    | +191.4%             |
| Aggiustamenti per ammortamenti               | 300      | 350      | 400      | 500      | 550      | 600      | +100%               |
| Variazioni nel capitale circolante           | -100     | -150     | -200     | -200     | -250     | -300     | +200%               |
| **Totale Flussi Operativi**                  | **900**  | **1,000** | **1,100** | **1,300** | **1,400** | **2,340** | +160%               |
| **Flussi di Cassa dalle Attività di Investimento** |          |          |          |          |          |          |                     |
| Acquisto di immobilizzazioni                 | -700     | -800     | -900     | -1,000   | -1,100   | -1,200   | +71.4%              |
| Investimenti in R&D                          | -300     | -350     | -400     | -500     | -550     | -600     | +66.7%              |
| **Totale Flussi Investimenti**               | **-1,000** | **-1,150** | **-1,300** | **-1,500** | **-1,650** | **-1,800** | +38.5%       |
| **Flussi di Cassa dalle Attività di Finanziamento** |          |          |          |          |          |          |                     |
| Emissione di nuove azioni                    | 0        | 0        | 0        | 500      | 500      | 500      | N/A                 |
| Rimborso debiti                              | -200     | -250     | -300     | -300     | -350     | -400     | +33.3%              |
| Dividendi pagati                             | -150     | -200     | -250     | -200     | -250     | -300     | +50%                |
| **Totale Flussi Finanziamento**              | **-350** | **-450** | **-550** | **0**    | **-100** | **-200** | +350%                |
| **Variazione Netta delle Disponibilità Liquide** | **-450** | **-600** | **-700** | **-200** | **-350** | **-660** | +185.7%              |
| Disponibilità liquide all'inizio anno        | 1,250    | 800      | 200      | -500     | -700     | -1,050   | N/A                 |
| Disponibilità liquide alla fine anno         | 800      | 200      | -500     | -700     | -1,050   | -1,710   | N/A                 |

##### **Indicatori di Performance ESG 2025**

| **Indicatore**                   | **Valore 2020** | **Valore 2021** | **Valore 2022** | **Valore 2023** | **Valore 2024** | **Valore 2025** | **Obiettivo 2026** | **Variazione (%)** |
|----------------------------------|-----------------|-----------------|-----------------|-----------------|-----------------|-----------------|---------------------|---------------------|
| Emissioni di CO2 (ton)           | 10,000          | 9,000           | 8,000           | 7,200           | 6,800           | 6,400           | 5,000               | -36%                |
| Percentuale Clienti Soddisfatti  | 85%             | 88%             | 90%             | 92%             | 93%             | 95%             | 95%                 | +10.6%               |
| Numero di Nuovi Mercati           | 2               | 3               | 4               | 5               | 5               | 5               | 5                   | 150%                |
| Investimento in R&D (%)           | 15%             | 16%             | 18%             | 20%             | 20%             | 20%             | 20%                 | +33.3%               |
| Ore di Formazione Totale          | 1,800           | 2,000           | 2,200           | 2,400           | 2,400           | 2,400           | 2,400               | +38.9%               |

----------

### **Dettagli Aggiuntivi su Agilae S.p.A.**

**Chi Siamo** _([https://www.agilae.it/chi-siamo/](https://www.agilae.it/chi-siamo/))_

Agilae S.p.A. è una società leader nel settore della consulenza tecnologica, specializzata in soluzioni innovative per le imprese. Fondata nel 2010, Agilae si distingue per la sua capacità di integrare tecnologie all'avanguardia con strategie di business personalizzate, supportando i clienti nella trasformazione digitale e nell'ottimizzazione dei processi aziendali.

**Servizi** _([https://www.agilae.it/servizi/](https://www.agilae.it/servizi/))_

-   **Consulenza Strategica:** Supporto nella definizione e implementazione di strategie aziendali orientate alla crescita sostenibile.
-   **Soluzioni IT Personalizzate:** Sviluppo di software su misura, gestione infrastrutture IT e implementazione di sistemi ERP.
-   **Cyber Security:** Protezione avanzata dei dati aziendali attraverso soluzioni di sicurezza informatica integrate.
-   **Formazione e Supporto:** Programmi di formazione per lo sviluppo delle competenze digitali del personale e supporto tecnico continuo.
-   **Progetti di Innovazione:** Collaborazione con start-up e aziende tecnologiche per lo sviluppo di progetti innovativi.

**Lavora con Noi** _([https://www.agilae.it/lavora-con-noi/](https://www.agilae.it/lavora-con-noi/))_

Agilae S.p.A. è sempre alla ricerca di talenti motivati e appassionati di tecnologia. Offriamo un ambiente di lavoro dinamico, opportunità di crescita professionale e un impegno costante verso la formazione e lo sviluppo delle competenze dei nostri dipendenti.

**Contatti** _([https://www.agilae.it/contatti/](https://www.agilae.it/contatti/))_

Per ulteriori informazioni o per contattare il nostro team, visita la nostra pagina dei contatti o utilizza i seguenti dettagli:

-   **Indirizzo:** Via Roma, 123, 00100 Roma RM, Italia
-   **Telefono:** +39 06 1234567
-   **Email:** [info@agilae.it](mailto:info@agilae.it)

----------

"""