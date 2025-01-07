# Documento Descrittivo del Progetto: Generazione Automatica del Bilancio di Sostenibilità

## Obiettivo del Progetto

Il progetto mira a automatizzare la creazione del Bilancio di Sostenibilità aziendale attraverso l'utilizzo di tecnologie avanzate di intelligenza artificiale. Sfruttando l'elaborazione del linguaggio naturale (NLP) e l'integrazione con modelli linguistici di ultima generazione, il sistema genera contenuti dettagliati, compila template predefiniti e produce report in formato HTML, arricchiti con grafici e tabelle pertinenti.

## Architettura Tecnica

L'architettura del progetto è composta da diverse componenti integrate:

-   **Frontend**: Un'applicazione web interattiva sviluppata con **Streamlit** per l'interfaccia utente.
-   **Backend**: Un'API RESTful costruita con **FastAPI** per gestire le richieste e orchestrare i processi.
-   **Database**: **MongoDB** per la memorizzazione dei dati, inclusi file caricati, descrizioni e risultati intermedi.
-   **AI Models**: Integrazione con modelli di linguaggio OpenAI per la generazione di contenuti.
-   **Vector Stores**: Utilizzo di **Chroma** per l'archiviazione e il recupero di informazioni testuali.
-   **Gestione Template**: Un sistema per la compilazione dinamica di template HTML attraverso il **TemplateManager**.
-   **Generazione Grafici**: Strumenti per creare e incorporare grafici nel report finale.

## Dettaglio delle Componenti

### 1. Frontend (Streamlit App)

-   **Interfaccia Utente**: Permette agli utenti di caricare documenti, inserire URL con descrizioni, e interagire con il sistema tramite una chat integrata.
-   **Caricamento File**: Supporta l'upload di file in vari formati (PDF, TXT, DOCX) per l'elaborazione.
-   **Session Management**: Utilizza un `session_id` per gestire le sessioni utente e organizzare i dati correlati.

### 2. Backend (FastAPI)

-   **Endpoint RESTful**: Fornisce vari endpoint per caricare documenti, configurare catene di elaborazione (chains), e gestire l'interazione con i modelli AI.
-   **Gestione Documenti**: Endpoint dedicati per la creazione di contesti, l'upload di file e la gestione dei vector stores.
-   **Integrazione con MongoDB**: Salva informazioni sui file caricati e le loro descrizioni in collezioni specifiche per sessione.

### 3. Database (MongoDB)

-   **Struttura dei Dati**: Ogni sessione ha un proprio database (`{session_id}_db`) con collezioni come `file_descriptions` per memorizzare informazioni sui file caricati.
-   **Querying**: Il sistema esegue query per recuperare dati necessari durante l'elaborazione e la generazione dei contenuti.

### 4. Modelli di Intelligenza Artificiale

-   **OpenAI GPT**: Utilizza modelli GPT-4 per l'elaborazione del linguaggio naturale, generando testi coerenti e pertinenti per le varie sezioni del report.
-   **Configurazione Dinamica**: I modelli vengono caricati e configurati dinamicamente in base alle esigenze, permettendo flessibilità e scalabilità.

### 5. Vector Stores (Chroma)

-   **Memorizzazione Vettoriale**: I documenti caricati vengono elaborati e convertiti in rappresentazioni vettoriali per un efficiente recupero delle informazioni.
-   **Ricerca Semantica**: Permette al sistema di effettuare ricerche avanzate nei contenuti dei documenti, migliorando la qualità e la pertinenza dei contenuti generati.

### 6. TemplateManager

-   **Gestione Template HTML**: Consente la compilazione dinamica di un template HTML predefinito del Bilancio di Sostenibilità.
-   **Sostituzione Placeholder**: I contenuti generati vengono inseriti nelle sezioni appropriate del template, utilizzando chiavi specifiche per identificare ogni sezione.
-   **Aggiornamento e Salvataggio**: Dopo la compilazione, il template aggiornato viene salvato e reso disponibile all'utente tramite un link diretto.

### 7. Generazione Grafici (GraphManager)

-   **Creazione Grafici**: Il sistema può generare vari tipi di grafici (a torta, a barre, lineari) basati sui dati estratti.
-   **Integrazione nel Report**: I grafici generati vengono salvati e integrati nel report HTML, arricchendo visivamente le informazioni presentate.

## Flusso di Lavoro

1.  **Upload dei Documenti**: L'utente carica uno o più documenti attraverso l'interfaccia Streamlit.
2.  **Elaborazione Iniziale**:
    -   Viene creato un contesto specifico per la sessione.
    -   I documenti vengono caricati nei vector stores e le informazioni vengono salvate in MongoDB.
3.  **Configurazione delle Catene di Elaborazione**:
    -   Viene configurata una chain per l'analisi dei documenti.
    -   Si carica il modello AI appropriato.
4.  **Interazione con l'Utente**:
    -   L'utente può interagire tramite chat, fornendo istruzioni specifiche.
    -   Il sistema utilizza la chat history per mantenere il contesto.
5.  **Generazione dei Contenuti**:
    -   Il modello AI genera contenuti per le varie sezioni del report, basandosi sui documenti caricati e sulle istruzioni dell'utente.
    -   Vengono creati grafici e tabelle se richiesto.
6.  **Compilazione del Template**:
    -   I contenuti generati vengono inseriti nel template HTML tramite il TemplateManager.
    -   Il report viene aggiornato e salvato.
7.  **Condivisione del Report**:
    -   Il report finale è accessibile all'utente tramite un link diretto, ospitato su un server specifico.
    -   I grafici e le risorse sono anch'essi ospitati e resi disponibili tramite URL.

## Hosting e Accessibilità

-   **Hosting dei File**: Tutti i file generati, inclusi il report e i grafici, sono ospitati all'indirizzo:
    
    ```
    http://35.205.92.199:8093/files/{session_id}/<nome_file>
    
    ```
    
-   **Accesso al Report**: Il Bilancio di Sostenibilità generato è disponibile come `bilancio_sostenibilita.html` e può essere visualizzato tramite il link:
    
    ```
    http://35.205.92.199:8093/files/{session_id}/bilancio_sostenibilita.html
    
    ```
    
-   **Sicurezza**: L'accesso ai file è gestito tramite sessioni uniche (`session_id`), garantendo che i dati siano isolati tra gli utenti.
    

## Innovazioni e Vantaggi Tecnici

-   **Automazione Avanzata**: Il sistema riduce drasticamente il tempo e le risorse necessarie per creare il Bilancio di Sostenibilità.
-   **Personalizzazione**: Grazie all'integrazione AI, i contenuti generati sono adattati ai documenti e alle esigenze specifiche dell'azienda.
-   **Interattività**: L'interfaccia chat permette un'interazione naturale e dinamica con il sistema.
-   **Scalabilità**: L'architettura modulare consente di gestire più sessioni e carichi di lavoro simultanei.
-   **Aggiornamento Continuo**: Il sistema può essere facilmente aggiornato con nuovi modelli AI e funzionalità aggiuntive.

