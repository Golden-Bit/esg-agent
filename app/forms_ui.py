import json
import streamlit as st
from datetime import datetime

# Definizione del questionario in una lista di dizionari con indice numerico incrementale
questions = [
    # 1. Azienda
    {
        "id": 1,
        "paragraph": "1",
        "sezione": "Azienda",
        "sotto_sezione": "",
        "domanda": "Presentazione azienda",
        "tipo": "text",
        "content_generation_rules": ""
    },
    # 2. Ambiente - 2.1 Biodiversità
    {
        "id": 2,
        "paragraph": "2.1.1",
        "sezione": "Ambiente",
        "sotto_sezione": "Biodiversità",
        "domanda": "L'attività aziendale ha avuto un impatto negativo sulle aree sensibili alla biodiversità durante il periodo in questione?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => Non generare testo; Se No => generare: 'L'attività aziendale non ha avuto un impatto negativo sulle aree sensibili alla biodiversità'."
    },
    {
        "id": 3,
        "paragraph": "2.1.2",
        "sezione": "Ambiente",
        "sotto_sezione": "Biodiversità",
        "domanda": "La tua organizzazione ha avuto una politica forestale per prevenire la deforestazione come risultato delle operazioni e/o azioni dell'entità, durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L’organizzazione ha avuto una politica forestale per prevenire la deforestazione come risultato delle operazioni e azioni dell'entità'; Se No => Non generare testo."
    },
    {
        "id": 4,
        "paragraph": "2.1.3",
        "sezione": "Ambiente",
        "sotto_sezione": "Biodiversità",
        "domanda": "Qual è la quota di superficie non vegetata, comprendente terreno, tetti, terrazze e muri, rispetto alla superficie totale dei lotti di tutti i beni aziendali, durante il periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Se il valore inserito > 0% => generare: 'La quota di superficie non vegetata, comprendente terreno, tetti, terrazze e muri, rispetto alla superficie totale dei lotti di tutti i beni aziendali è del X%'; Se il valore è 0% => Non generare testo."
    },
    {
        "id": 5,
        "paragraph": "2.1.4",
        "sezione": "Ambiente",
        "sotto_sezione": "Biodiversità",
        "domanda": "L'azienda ha avuto una politica di protezione della biodiversità che coprisse i siti operativi posseduti, affittati, gestiti in o adiacenti a un'area protetta o a un'area di elevato valore per la biodiversità al di fuori delle aree protette, durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha avuto una politica di protezione della biodiversità che coprisse i siti operativi posseduti, affittati, gestiti in o adiacenti a un'area protetta o a un'area di elevato valore per la biodiversità al di fuori delle aree protette'; Se No => Non generare testo."
    },
    {
        "id": 6,
        "paragraph": "2.1.5",
        "sezione": "Ambiente",
        "sotto_sezione": "Biodiversità",
        "domanda": "Le operazioni dell'organizzazione hanno avuto un impatto negativo sulle specie minacciate sulla base della Lista Rossa dell'UICN e/o della Lista Rossa Europea, durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => Non generare testo; Se No => generare: 'Le operazioni dell'organizzazione non hanno avuto un impatto negativo sulle specie minacciate sulla base della Lista Rossa dell'UICN e/o della Lista Rossa Europea'."
    },
    # 2.2 Impronta di carbonio
    {
        "id": 7,
        "paragraph": "2.2.1",
        "sezione": "Ambiente",
        "sotto_sezione": "Impronta di carbonio",
        "domanda": "L'azienda ha intrapreso iniziative di riduzione delle emissioni di carbonio volte ad allinearsi con l'Accordo di Parigi, durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha intrapreso iniziative di riduzione delle emissioni di carbonio volte ad allinearsi con l'Accordo di Parigi'; Se No => Non generare testo."
    },
    {
        "id": 8,
        "paragraph": "2.2.2",
        "sezione": "Ambiente",
        "sotto_sezione": "Impronta di carbonio",
        "domanda": "L'azienda è stata attiva nel settore dei combustibili fossili, durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda è attiva nel settore dei combustibili fossili'; Se No => Non generare testo."
    },
    # 2.3 Emissioni di gas serra
    {
        "id": 9,
        "paragraph": "2.3.1",
        "sezione": "Ambiente",
        "sotto_sezione": "Emissioni di gas serra",
        "domanda": "Quante tonnellate di diossido di carbonio di gas serra di 'Scope 1' (CO₂ equivalente) ha emesso l'azienda durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se un valore X è fornito => generare: 'L’azienda ha emesso X tonnellate di diossido di carbonio di gas serra di “Scope 1”'; altrimenti, non generare testo."
    },
    {
        "id": 10,
        "paragraph": "2.3.2",
        "sezione": "Ambiente",
        "sotto_sezione": "Emissioni di gas serra",
        "domanda": "Quante tonnellate di diossido di carbonio di gas serra di 'Scope 1' (CO₂ equivalente) sono state generate da attività immobiliari durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se un valore X è fornito => generare: 'X tonnellate di diossido di carbonio di gas serra di “Scope 1” sono state generate da attività immobiliari'; altrimenti, non generare testo."
    },
    {
        "id": 11,
        "paragraph": "2.3.3",
        "sezione": "Ambiente",
        "sotto_sezione": "Emissioni di gas serra",
        "domanda": "Quante tonnellate di diossido di carbonio (CO₂ equivalente) di gas serra di 'Scope 2' ha emesso l'azienda durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se un valore X è fornito => generare: 'L’azienda ha emesso X tonnellate di diossido di carbonio di gas serra di “Scope 2”'; altrimenti, non generare testo."
    },
    {
        "id": 12,
        "paragraph": "2.3.4",
        "sezione": "Ambiente",
        "sotto_sezione": "Emissioni di gas serra",
        "domanda": "Quante tonnellate di diossido di carbonio di gas serra di 'Scope 2' (CO₂ equivalente) sono state generate da attività immobiliari durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se un valore X è fornito => generare: 'X tonnellate di diossido di carbonio di gas serra di “Scope 2” sono state generate da attività immobiliari'; altrimenti, non generare testo."
    },
    {
        "id": 13,
        "paragraph": "2.3.5",
        "sezione": "Ambiente",
        "sotto_sezione": "Emissioni di gas serra",
        "domanda": "Quante tonnellate di diossido di carbonio (CO₂ equivalente) di gas serra di 'Scope 3' ha emesso l'azienda durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se un valore X è fornito => generare: 'L’azienda ha emesso X tonnellate di diossido di carbonio di gas serra di “Scope 3”'; altrimenti, non generare testo."
    },
    {
        "id": 14,
        "paragraph": "2.3.6",
        "sezione": "Ambiente",
        "sotto_sezione": "Emissioni di gas serra",
        "domanda": "Quante tonnellate di diossido di carbonio di gas serra di 'Scope 3' (CO₂ equivalente) sono state generate da attività immobiliari durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se un valore X è fornito => generare: 'X tonnellate di diossido di carbonio di gas serra di “Scope 3” sono state generate da attività immobiliari'; altrimenti, non generare testo."
    },
    {
        "id": 15,
        "paragraph": "2.3.7",
        "sezione": "Ambiente",
        "sotto_sezione": "Emissioni di gas serra",
        "domanda": "In quali settori climatici ad alto impatto è stata attiva l'azienda durante il periodo?",
        "tipo": "select",
        "opzioni": [
            "Settore Energetico",
            "Settore dell’Industria Pesante",
            "Agricoltura",
            "Settore Immobiliare",
            "Servizi Pubblici",
            "Settore Alimentare e delle Bevande",
            "Settore Beni di Consumo",
            "Settore Farmaceutico",
            "Nessuno dei precedenti"
        ],
        "content_generation_rules": "Se la risposta è uno dei settori (tranne 'Nessuno dei precedenti') => generare: 'L’azienda attiva nel settore <risposta>'; se 'Nessuno dei precedenti' => non generare testo."
    },
    {
        "id": 16,
        "paragraph": "2.3.8",
        "sezione": "Ambiente",
        "sotto_sezione": "Emissioni di gas serra",
        "domanda": "L'azienda ha una data obiettivo per raggiungere le emissioni nette zero di GES durante il periodo? (Seleziona 'Sì' e indica la data)",
        "tipo": "date_categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha come obiettivo di raggiungere le emissioni zero di gas serra entro il GG/MM/AAAA' (con la data specificata); Se No => non generare testo."
    },
    # 2.4 Altre emissioni
    {
        "id": 17,
        "paragraph": "2.4.1",
        "sezione": "Ambiente",
        "sotto_sezione": "Altre emissioni",
        "domanda": "L'azienda ha svolto operazioni e/o è stata coinvolta nella produzione di pesticidi e di altri prodotti agrochimici, durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'L'azienda non ha svolto operazioni e non è stata coinvolta nella produzione di pesticidi e di altri prodotti agrochimici'."
    },
    {
        "id": 18,
        "paragraph": "2.4.2",
        "sezione": "Ambiente",
        "sotto_sezione": "Altre emissioni",
        "domanda": "Quanti inquinanti atmosferici ha generato l'azienda durante i processi di approvvigionamento della produzione, durante il periodo? (in tonnellate)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quota di inquinanti atmosferici generati durante i processi di approvvigionamento della produzione è X tonnellate'; se X = 0 => non generare testo."
    },
    {
        "id": 19,
        "paragraph": "2.4.3",
        "sezione": "Ambiente",
        "sotto_sezione": "Altre emissioni",
        "domanda": "Quanti inquinanti inorganici ha generato l'azienda a seguito delle sue attività, durante il periodo? (in tonnellate)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quota di inquinanti inorganici generati a seguito delle attività di impresa è X tonnellate'; se X = 0 => non generare testo."
    },
    {
        "id": 20,
        "paragraph": "2.4.4",
        "sezione": "Ambiente",
        "sotto_sezione": "Altre emissioni",
        "domanda": "Quante sostanze che impoveriscono l'ozono ha emesso l'azienda a seguito delle sue attività, durante il periodo? (in tonnellate)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quota di sostanze che impoveriscono l’ozono emesse dall’azienda è X tonnellate'; se X = 0 => non generare testo."
    },
    # 2.5 Consumo energetico
    {
        "id": 21,
        "paragraph": "2.5.1",
        "sezione": "Ambiente",
        "sotto_sezione": "Consumo energetico",
        "domanda": "Quanta energia ha consumato l'azienda durante il periodo considerato? (in kWh)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quantità totale di energia consumata è stata X kWh'; se X = 0 => non generare testo."
    },
    {
        "id": 22,
        "paragraph": "2.5.2",
        "sezione": "Ambiente",
        "sotto_sezione": "Consumo energetico",
        "domanda": "Qual è stata l'intensità del consumo di energia dell'azienda, in GWh per milione di euro di ricavi, nel periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'L'intensità del consumo di energia è X GWh/M€'; se X = 0 => non generare testo."
    },
    {
        "id": 23,
        "paragraph": "2.5.3",
        "sezione": "Ambiente",
        "sotto_sezione": "Consumo energetico",
        "domanda": "Quanta energia non rinnovabile ha consumato l'azienda durante il periodo considerato? (in kWh)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quantità di energia non rinnovabile consumata è stata X kWh'; se X = 0 => non generare testo."
    },
    {
        "id": 24,
        "paragraph": "2.5.4",
        "sezione": "Ambiente",
        "sotto_sezione": "Consumo energetico",
        "domanda": "Quale proporzione dell'energia totale consumata dall'azienda durante il periodo era non rinnovabile? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La proporzione di energia non rinnovabile consumata è stata X%'; se X = 0 => non generare testo."
    },
    {
        "id": 25,
        "paragraph": "2.5.5",
        "sezione": "Ambiente",
        "sotto_sezione": "Consumo energetico",
        "domanda": "Quanta energia rinnovabile ha consumato l'azienda durante il periodo considerato? (in kWh)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'Il consumo di energia rinnovabile è stato pari a X kWh'; se X = 0 => non generare testo."
    },
    # 2.6 Terra
    {
        "id": 26,
        "paragraph": "2.6.1",
        "sezione": "Ambiente",
        "sotto_sezione": "Terra",
        "domanda": "L'azienda ha svolto attività che causano degrado del suolo, desertificazione o sigillatura del suolo, durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'L'azienda non ha svolto attività che causano degrado del suolo, desertificazione o sigillatura del suolo'."
    },
    {
        "id": 27,
        "paragraph": "2.6.2",
        "sezione": "Ambiente",
        "sotto_sezione": "Terra",
        "domanda": "L'azienda ha avuto pratiche o politiche di agricoltura sostenibile o di gestione del territorio durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha avuto pratiche e politiche di agricoltura sostenibile e di gestione del territorio'; Se No => non generare testo."
    },
    {
        "id": 28,
        "paragraph": "2.6.3",
        "sezione": "Ambiente",
        "sotto_sezione": "Terra",
        "domanda": "L'azienda ha avuto pratiche o politiche sostenibili per oceani e mari, durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha avuto pratiche e politiche sostenibili per oceani e mari'; Se No => non generare testo."
    },
    # 2.7 Gestione dei rifiuti
    {
        "id": 29,
        "paragraph": "2.7.1",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dei rifiuti",
        "domanda": "Quanti rifiuti pericolosi ha prodotto l'azienda durante il periodo? (in tonnellate)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quantità prodotta di rifiuti pericolosi è stata di X tonnellate'; se X = 0 => non generare testo."
    },
    {
        "id": 30,
        "paragraph": "2.7.2",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dei rifiuti",
        "domanda": "Quanti rifiuti non riciclati ha generato l'azienda durante il periodo? (in tonnellate)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quantità prodotta di rifiuti non riciclati è stata di X tonnellate'; se X = 0 => non generare testo."
    },
    {
        "id": 31,
        "paragraph": "2.7.3",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dei rifiuti",
        "domanda": "La tua azienda ha avuto una politica di smaltimento dei rifiuti per gli uffici durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha avuto una politica di smaltimento dei rifiuti per gli uffici'; Se No => non generare testo."
    },
    {
        "id": 32,
        "paragraph": "2.7.4",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dei rifiuti",
        "domanda": "Quale percentuale di materie prime edilizie (esclusi materiali recuperati, riciclati e di origine biologica) ha utilizzato l'azienda, rispetto al peso totale dei materiali edilizi utilizzati nelle nuove costruzioni e nelle ristrutturazioni importanti, durante il periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La percentuale di materie prime edilizie (esclusi materiali recuperati, riciclati e di origine biologica) che ha utilizzato l'azienda, rispetto al peso totale dei materiali edilizi utilizzati nelle nuove costruzioni e nelle ristrutturazioni importanti, è stata X%'; se X = 0 => non generare testo."
    },
    {
        "id": 33,
        "paragraph": "2.7.5",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dei rifiuti",
        "domanda": "Qual è stata la quota di attività immobiliari non dotate di impianti per il trattamento dei rifiuti e non coperte da un contratto di recupero o riciclaggio dei rifiuti, durante il periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quota di attività immobiliari non dotate di impianti per il trattamento dei rifiuti e non coperte da un contratto di recupero o riciclaggio dei rifiuti è stata X%'; se X = 0 => non generare testo."
    },
    # 2.8 Gestione dell'acqua
    {
        "id": 34,
        "paragraph": "2.8.1",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dell'acqua",
        "domanda": "Quante tonnellate di 'sostanze prioritarie' l'azienda ha immesso direttamente in acqua durante il periodo considerato?",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quantità di \"sostanze prioritarie\" che l'azienda ha immesso direttamente in acqua durante il periodo considerato è X tonnellate'; se X = 0 => non generare testo."
    },
    {
        "id": 35,
        "paragraph": "2.8.2",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dell'acqua",
        "domanda": "L'azienda era situata in aree ad alto stress idrico senza una politica di gestione dell'acqua durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'L'azienda non è situata in aree ad alto stress idrico'."
    },
    {
        "id": 36,
        "paragraph": "2.8.3",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dell'acqua",
        "domanda": "Quanta acqua consumata dall'azienda è stata riciclata e riutilizzata, durante il periodo? (in m³)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quantità di acqua riciclata e riutilizzata dall’azienda è stata di X m³'; se X = 0 => non generare testo."
    },
    {
        "id": 37,
        "paragraph": "2.8.4",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dell'acqua",
        "domanda": "Quanta acqua ha consumato l'azienda durante il periodo considerato? (in m³)",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'La quantità di acqua consumata dall’azienda è stata di X m³'; se X = 0 => non generare testo."
    },
    {
        "id": 38,
        "paragraph": "2.8.5",
        "sezione": "Ambiente",
        "sotto_sezione": "Gestione dell'acqua",
        "domanda": "L'azienda aveva una politica di gestione dell'acqua relativa alla metodologia di utilizzo e scarico dell'acqua durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha una politica di gestione dell'acqua relativa alla metodologia di utilizzo e scarico dell'acqua'; se No => non generare testo."
    },
    # 3. Sociale - 3.1 Diversità sociale
    {
        "id": 39,
        "paragraph": "3.1.1",
        "sezione": "Sociale",
        "sotto_sezione": "Diversità sociale",
        "domanda": "Qual è stata la differenza salariale media tra uomini e donne durante il periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Generare: 'La differenza salariale media tra uomini e donne è X%'."
    },
    {
        "id": 40,
        "paragraph": "3.1.2",
        "sezione": "Sociale",
        "sotto_sezione": "Diversità sociale",
        "domanda": "Qual era la proporzione di individui nel consiglio che si identificano come donne, misurata alla fine del periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Generare: 'La proporzione di donne nel consiglio è X%'."
    },
    {
        "id": 41,
        "paragraph": "3.1.3",
        "sezione": "Sociale",
        "sotto_sezione": "Diversità sociale",
        "domanda": "L'azienda ha avuto una politica per promuovere l'uguaglianza di opportunità e la diversità durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha una politica per promuovere l'uguaglianza di opportunità e la diversità'; se No => non generare testo."
    },
    {
        "id": 42,
        "paragraph": "3.1.4",
        "sezione": "Sociale",
        "sotto_sezione": "Diversità sociale",
        "domanda": "L'azienda ha offerto formazione sulla diversità di genere durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha offerto formazione sulla diversità di genere durante il periodo'; se No => non generare testo."
    },
    {
        "id": 43,
        "paragraph": "3.1.5",
        "sezione": "Sociale",
        "sotto_sezione": "Diversità sociale",
        "domanda": "Qual era la proporzione di individui nell'azienda che si identificano come donne, misurata alla fine del periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Generare: 'La proporzione di donne nell’azienda è X%'."
    },
    # 3.2 Questioni relative ai dipendenti
    {
        "id": 44,
        "paragraph": "3.2.1",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "L'azienda aveva una politica scritta anti-molestie che copriva tutti i suoi dipendenti sul posto di lavoro durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha avuto una politica scritta anti-molestie che copriva tutti i suoi dipendenti sul posto di lavoro'; se No => non generare testo."
    },
    {
        "id": 45,
        "paragraph": "3.2.2",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "Qual è il rapporto tra la retribuzione totale annuale per la persona meglio retribuita e la retribuzione totale annuale mediana per tutti i dipendenti durante il periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Generare: 'Il rapporto tra la retribuzione totale annuale per la persona meglio retribuita e la retribuzione totale annuale mediana per tutti i dipendenti è X%'."
    },
    {
        "id": 46,
        "paragraph": "3.2.3",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "L'azienda è stata esposta ad armi controverse durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'L'azienda non è stata esposta ad armi controverse'."
    },
    {
        "id": 47,
        "paragraph": "3.2.4",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "Gli uffici dell'azienda erano accessibili alle persone con disabilità fisica (es. rampa, ascensore, accesso disabili, bagno adattato) durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'Gli uffici dell'azienda sono accessibili alle persone con disabilità fisica (cioè rampa, ascensore, accesso disabili, bagno adattato)'; se No => non generare testo."
    },
    {
        "id": 48,
        "paragraph": "3.2.5",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "Quanti incidenti di discriminazione sul luogo di lavoro sono stati segnalati durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Generare: 'Sono stati segnalati X incidenti di discriminazione sul luogo di lavoro'."
    },
    {
        "id": 49,
        "paragraph": "3.2.6",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "Quanti incidenti di discriminazione sul luogo di lavoro che hanno portato a sanzioni sono stati segnalati durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'Di questi, X incidenti di discriminazione sul luogo di lavoro hanno portato a sanzioni'; se X = 0 => non generare testo."
    },
    {
        "id": 50,
        "paragraph": "3.2.7",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "Qual è stato il tasso di turnover dei dipendenti durante il periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Generare: 'Il tasso di turnover dei dipendenti è X%'."
    },
    {
        "id": 51,
        "paragraph": "3.2.8",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "L’azienda ha avuto un codice di condotta per i fornitori (contro condizioni di lavoro insicure, lavoro precario, lavoro minorile e lavoro forzato)?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L’azienda ha avuto un codice di condotta per i fornitori contro condizioni di lavoro insicure, lavoro precario, lavoro minorile e lavoro forzato'; se No => non generare testo."
    },
    {
        "id": 52,
        "paragraph": "3.2.9",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "L'azienda ha attivato processi per rimediare agli impatti negativi e canali per i propri lavoratori per sollevare preoccupazioni con un meccanismo di gestione delle lamentele/reclami durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L’azienda ha attivato processi per rimediare agli impatti negativi e canali per i propri lavoratori per sollevare preoccupazioni con un meccanismo di gestione delle lamentele e reclami'; se No => non generare testo."
    },
    {
        "id": 53,
        "paragraph": "3.2.10",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "Qual era la percentuale di dipendenti che guadagnavano il salario minimo rispetto ai salari medi dei lavoratori a tempo pieno durante il periodo? (in %)",
        "tipo": "numeric",
        "content_generation_rules": "Generare: 'La proporzione di dipendenti che guadagnano il salario minimo rispetto ai salari medi dei lavoratori a tempo pieno è X%'."
    },
    {
        "id": 54,
        "paragraph": "3.2.11",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "L'azienda aveva processi e meccanismi di conformità per monitorare i principi del Global Compact delle Nazioni Unite e le Linee guida OCSE durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L’azienda ha attivato processi e meccanismi di conformità per monitorare la conformità con i principi del Global Compact delle Nazioni Unite e le Linee guida OCSE'; se No => non generare testo."
    },
    {
        "id": 55,
        "paragraph": "3.2.12",
        "sezione": "Sociale",
        "sotto_sezione": "Questioni relative ai dipendenti",
        "domanda": "L'azienda è stata coinvolta in violazioni dei principi del Global Compact delle Nazioni Unite e delle Linee guida OCSE durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'L’azienda non è stata coinvolta in violazioni dei principi del Global Compact delle Nazioni Unite e delle Linee guida OCSE'."
    },
    # 3.3 Salute e sicurezza
    {
        "id": 56,
        "paragraph": "3.3.1",
        "sezione": "Sociale",
        "sotto_sezione": "Salute e sicurezza",
        "domanda": "L'azienda ha fornito copertura assicurativa sanitaria o strutture (in loco/vicino al luogo di lavoro) per i dipendenti durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha fornito copertura assicurativa sanitaria e strutture vicino al luogo di lavoro per i dipendenti, sia come opzione per i dipendenti a prezzo scontato che come beneficio finanziato dall'azienda'; se No => non generare testo."
    },
    {
        "id": 57,
        "paragraph": "3.3.2",
        "sezione": "Sociale",
        "sotto_sezione": "Salute e sicurezza",
        "domanda": "Quanti giorni lavorativi equivalenti totali sono stati persi a causa di lesioni, incidenti, morti o malattie correlate al lavoro, durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'X giorni lavorativi equivalenti totali sono stati persi a causa di lesioni, incidenti, morti o malattie correlate al lavoro'; se X = 0 => generare: 'Nel periodo di riferimento non ci sono stati giorni lavorativi persi a causa di lesioni, incidenti, morti o malattie correlate al lavoro'."
    },
    {
        "id": 58,
        "paragraph": "3.3.3",
        "sezione": "Sociale",
        "sotto_sezione": "Salute e sicurezza",
        "domanda": "Quanti incidenti sul lavoro sono avvenuti durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'Sono avvenuti X incidenti sul lavoro'; se X = 0 => generare: 'Non sono avvenuti incidenti sul lavoro'."
    },
    {
        "id": 59,
        "paragraph": "3.3.4",
        "sezione": "Sociale",
        "sotto_sezione": "Salute e sicurezza",
        "domanda": "Durante il periodo, l'azienda aveva politiche per sostenere l'equilibrio tra lavoro e vita privata?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L’azienda ha delle politiche per sostenere le pratiche e la cultura del luogo di lavoro in termini di equilibrio tra lavoro e vita privata'; se No => non generare testo."
    },
    {
        "id": 60,
        "paragraph": "3.3.5",
        "sezione": "Sociale",
        "sotto_sezione": "Salute e sicurezza",
        "domanda": "Durante il periodo, l'azienda ha avuto una politica di prevenzione degli incidenti sul lavoro?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L’azienda ha avuto una politica di prevenzione degli incidenti sul lavoro'; se No => non generare testo."
    },
    # 3.4 Diritti umani
    {
        "id": 61,
        "paragraph": "3.4.1",
        "sezione": "Sociale",
        "sotto_sezione": "Diritti umani",
        "domanda": "In quanti casi di gravi problemi e incidenti relativi ai diritti umani è stata coinvolta l'azienda, durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se X > 0 => generare: 'Ci sono stati X casi di gravi problemi e incidenti relativi ai diritti umani'; se X = 0 => non generare testo."
    },
    {
        "id": 62,
        "paragraph": "3.4.2",
        "sezione": "Sociale",
        "sotto_sezione": "Diritti umani",
        "domanda": "L'azienda è stata esposta a operazioni e fornitori a rischio significativo di incidenti di lavoro minorile?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'Non c’è stata esposizione a operazioni e fornitori a rischio significativo di incidenti di lavoro minorile esposti a lavori pericolosi in termini di aree geografiche o tipo di operazione'."
    },
    {
        "id": 63,
        "paragraph": "3.4.3",
        "sezione": "Sociale",
        "sotto_sezione": "Diritti umani",
        "domanda": "L'azienda è stata esposta a operazioni e fornitori a rischio significativo di lavoro forzato?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'Non c’è stata esposizione a operazioni e fornitori a rischio significativo di lavoro forzato o obbligatorio in termini di aree geografiche e/o tipo di operazione'."
    },
    {
        "id": 64,
        "paragraph": "3.4.4",
        "sezione": "Sociale",
        "sotto_sezione": "Diritti umani",
        "domanda": "L'azienda ha avuto una dichiarazione di politica sui diritti umani in linea con i Principi guida delle Nazioni Unite?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L’azienda ha avuto una dichiarazione di politica sui diritti umani in linea con i Principi guida delle Nazioni Unite su imprese e diritti umani'; se No => non generare testo."
    },
    {
        "id": 65,
        "paragraph": "3.4.5",
        "sezione": "Sociale",
        "sotto_sezione": "Diritti umani",
        "domanda": "L'azienda ha adottato una procedura di due diligence per identificare, prevenire, mitigare e affrontare gli impatti negativi sui diritti umani durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'È stata adottata una procedura di due diligence per identificare, prevenire, mitigare e affrontare gli impatti negativi sui diritti umani'; se No => non generare testo."
    },
    {
        "id": 66,
        "paragraph": "3.4.6",
        "sezione": "Sociale",
        "sotto_sezione": "Diritti umani",
        "domanda": "L'azienda ha messo in atto processi e misure per prevenire la tratta di esseri umani nelle sue operazioni e catene di fornitura globali?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'Sono stati messi in atto processi e misure per prevenire la tratta di esseri umani all'interno delle operazioni e catene di fornitura globali'; se No => non generare testo."
    },
    # 4. Governance - 4.1 Etica aziendale
    {
        "id": 67,
        "paragraph": "4.1.1",
        "sezione": "Governance",
        "sotto_sezione": "Etica aziendale",
        "domanda": "Durante il periodo di riferimento, l’azienda è stata coinvolta in cause legali o reati fiscali oggetto di indagine?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'Non c’è stato un coinvolgimento in cause legali o reati fiscali oggetto di indagine da parte di un procedimento giudiziario/normativo'."
    },
    {
        "id": 68,
        "paragraph": "4.1.2",
        "sezione": "Governance",
        "sotto_sezione": "Etica aziendale",
        "domanda": "Durante il periodo, l'azienda ha avuto politiche sulla protezione dei segnalatori?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'Sono state adottate politiche sulla protezione dei segnalatori'; se No => non generare testo."
    },
    # 4.2 Governance aziendale
    {
        "id": 69,
        "paragraph": "4.2.1",
        "sezione": "Governance",
        "sotto_sezione": "Governance aziendale",
        "domanda": "Durante il periodo, l'azienda ha avuto un comitato responsabile della governance aziendale?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'C’è un comitato responsabile della governance aziendale'; se No => non generare testo."
    },
    {
        "id": 70,
        "paragraph": "4.2.2",
        "sezione": "Governance",
        "sotto_sezione": "Governance aziendale",
        "domanda": "L'organo di governance aziendale è stato sottoposto a un audit esterno da parte di un fornitore di servizi di revisione di terze parti?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'organo di governance aziendale stato sottoposto a un audit esterno da parte di un fornitore di servizi di revisione di terze parti legalmente autorizzato e accreditato'; se No => non generare testo."
    },
    # 4.3 Corruzione e tangenti
    {
        "id": 71,
        "paragraph": "4.3.1",
        "sezione": "Governance",
        "sotto_sezione": "Corruzione e tangenti",
        "domanda": "L'azienda ha identificato insufficienze nelle azioni intraprese per affrontare le violazioni delle procedure di anticorruzione e anti-corruttela durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => non generare testo; Se No => generare: 'Non sono state identificate insufficienze nelle azioni intraprese per affrontare le violazioni delle procedure e degli standard di anticorruzione e anti-corruttela'."
    },
    {
        "id": 72,
        "paragraph": "4.3.2",
        "sezione": "Governance",
        "sotto_sezione": "Corruzione e tangenti",
        "domanda": "L'azienda aveva politiche anticorruzione e anti-corruttela conformi alla Convenzione delle Nazioni Unite contro la corruzione durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L’azienda ha definito politiche anticorruzione e anti-corruttela conformi alla Convenzione delle Nazioni Unite contro la corruzione'; se No => non generare testo."
    },
    {
        "id": 73,
        "paragraph": "4.3.3",
        "sezione": "Governance",
        "sotto_sezione": "Corruzione e tangenti",
        "domanda": "Quante condanne e multe per violazioni delle leggi anticorruzione e anti-corruttela ha incontrato l'azienda, durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se X = 0 => generare: 'Non sono state ricevute condanne o multe per violazioni delle leggi anticorruzione e anti-corruttela'; se X > 0 => generare: 'Sono state ricevute X condanne e multe per violazioni delle leggi anticorruzione e anti-corruttela'."
    },
    # 4.4 Privacy e sicurezza dei dati
    {
        "id": 74,
        "paragraph": "4.4.1",
        "sezione": "Governance",
        "sotto_sezione": "Privacy e sicurezza dei dati",
        "domanda": "In quante procedure legali associate alla privacy dell'utente l'azienda è stata coinvolta durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se X = 0 => generare: 'L’azienda non è stata coinvolta in procedure legali associate alla privacy dell'utente'; se X > 0 => generare: 'L’azienda è stata coinvolta in X procedure legali associate alla privacy dell'utente'."
    },
    {
        "id": 75,
        "paragraph": "4.4.2",
        "sezione": "Governance",
        "sotto_sezione": "Privacy e sicurezza dei dati",
        "domanda": "Quante violazioni di dati (fughe, furti, perdite) ha subito l'azienda durante il periodo?",
        "tipo": "numeric",
        "content_generation_rules": "Se X = 0 => generare: 'Non ci sono state violazioni di dati, come fughe di notizie, furti o perdite di dati dei clienti'; se X > 0 => generare: 'Ci sono state X violazioni di dati, come fughe di notizie, furti o perdite di dati dei clienti'."
    },
    {
        "id": 76,
        "paragraph": "4.4.3",
        "sezione": "Governance",
        "sotto_sezione": "Privacy e sicurezza dei dati",
        "domanda": "L'azienda ha adottato misure di sicurezza specifiche per proteggersi dalle minacce e dai rischi di sicurezza informatica durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'Sono state adottate misure di sicurezza specifiche per proteggersi dalle minacce e dai rischi di sicurezza informatica'; se No => non generare testo."
    },
    {
        "id": 77,
        "paragraph": "4.4.4",
        "sezione": "Governance",
        "sotto_sezione": "Privacy e sicurezza dei dati",
        "domanda": "L'azienda aveva piattaforme conformi al GDPR e aveva nominato un DPO durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'Sono state utilizzate piattaforme conformi al GDPR e aveva nominato un DPO (Data Protection Officer)'; se No => non generare testo."
    },
    # 4.5 Sostenibilità della catena di fornitura
    {
        "id": 78,
        "paragraph": "4.5.1",
        "sezione": "Governance",
        "sotto_sezione": "Sostenibilità della catena di fornitura",
        "domanda": "L'azienda ha dimostrato trasparenza e tracciabilità nelle sue catene di approvvigionamento durante il periodo?",
        "tipo": "categorical",
        "opzioni": ["Sì", "No"],
        "content_generation_rules": "Se Sì => generare: 'L'azienda ha dimostrato trasparenza e tracciabilità nelle sue catene di approvvigionamento'; se No => non generare testo."
    }
]


def merge_questions_with_responses(questions, responses):
    """
    Riceve in input una lista di oggetti che compongono le domande del questionario (questions)
    e un dizionario contenente le risposte dell'utente (responses).
    Restituisce una nuova lista di oggetti in cui ogni oggetto domanda ha aggiunto il campo 'ANSWER'
    che contiene la risposta corrispondente presa dal dizionario responses.

    Parametri:
    - questions: lista di dizionari, ciascuno rappresenta una domanda del questionario.
    - responses: dizionario in cui le chiavi sono gli id delle domande (come stringhe) e i valori sono le risposte dell'utente.

    Ritorno:
    - merged_questions: lista di dizionari, ciascuno con un campo aggiuntivo 'ANSWER' contenente la risposta.
    """
    merged_questions = []
    for question in questions:
        # Convertiamo l'id in stringa per cercarlo nel dizionario delle risposte
        q_id = str(question["id"])
        # Creiamo una copia della domanda per non modificare l'oggetto originale
        question_with_answer = question.copy()
        # Aggiungiamo il campo 'ANSWER' con la risposta trovata, oppure None se non esiste
        question_with_answer["ANSWER"] = responses.get(q_id, None)
        merged_questions.append(question_with_answer)
    return merged_questions

def load_questions():
    return questions

def save_responses(responses, output_path):
    """Salva le risposte date in un file JSON."""
    with open(output_path, 'w', encoding="utf-8") as file:
        json.dump(responses, file, indent=4, ensure_ascii=False)
def get_default_index(options, saved_value):
    """
    Restituisce l'indice corrispondente a saved_value se esiste nelle opzioni,
    altrimenti restituisce l'indice di "NESSUNA RISPOSTA".
    """
    if saved_value in options:
        return options.index(saved_value)
    else:
        return options.index("NESSUNA RISPOSTA") if "NESSUNA RISPOSTA" in options else 0

def render_questionnaire(questions, saved_responses=None):
    """
    Renderizza il questionario ESG su Streamlit, mantenendo le risposte salvate.
    Per i campi categorici, date e select, se è presente una risposta salvata viene usata, altrimenti viene usato il default "NESSUNA RISPOSTA".
    """
    responses = {}
    current_section = None
    current_sub_section = None

    st.title("Questionario ESG")

    for question in questions:
        question_id = str(question["id"])
        # Per ogni domanda, se esiste una risposta salvata, altrimenti default "NESSUNA RISPOSTA"
        previous_answer = saved_responses.get(question_id, "NESSUNA RISPOSTA") if saved_responses else "NESSUNA RISPOSTA"

        # Mostra la sezione se cambia
        if question['sezione'] != current_section:
            st.markdown(f"<h2 style='font-size: 24px; margin-top: 20px;'>{question['sezione']}</h2>", unsafe_allow_html=True)
            current_section = question['sezione']
            current_sub_section = None

        # Mostra la sottosezione se cambia e se presente
        if question['sotto_sezione'] != current_sub_section:
            if question['sotto_sezione']:
                st.markdown(f"<h3 style='font-size: 20px; margin-top: 10px;'>{question['sotto_sezione']}</h3>", unsafe_allow_html=True)
            current_sub_section = question['sotto_sezione']

        # Mostra la domanda
        st.markdown(f"<p style='font-size: 16px; margin-top: 10px;'>{question_id}. {question['domanda']}</p>", unsafe_allow_html=True)

        # Rendering in base al tipo di domanda
        if question["tipo"] == "categorical":
            options = ["NESSUNA RISPOSTA"] + question["opzioni"] if "NESSUNA RISPOSTA" not in question["opzioni"] else question["opzioni"]
            default_index = get_default_index(options, previous_answer)
            responses[question_id] = st.radio(
                label="",
                options=options,
                index=default_index,
                key=f"question_{question_id}"
            )
        elif question["tipo"] == "numeric":
            # Per campi numerici usiamo text_input per consentire "NESSUNA RISPOSTA" se l'utente lo desidera
            responses[question_id] = st.text_input(
                label="",
                value=str(previous_answer) if previous_answer != 0 else "NESSUNA RISPOSTA",
                key=f"question_{question_id}"
            )
        elif question["tipo"] == "text":
            responses[question_id] = st.text_area(
                label="",
                value=previous_answer if previous_answer != "" else "NESSUNA RISPOSTA",
                key=f"question_{question_id}"
            )
        elif question["tipo"] == "select":
            options = ["NESSUNA RISPOSTA"] + question["opzioni"] if "NESSUNA RISPOSTA" not in question["opzioni"] else question["opzioni"]
            default_index = get_default_index(options, previous_answer)
            responses[question_id] = st.selectbox(
                label="",
                options=options,
                index=default_index,
                key=f"question_{question_id}"
            )
        elif question["tipo"] == "date_categorical":
            options = ["NESSUNA RISPOSTA"] + question["opzioni"] if "NESSUNA RISPOSTA" not in question["opzioni"] else question["opzioni"]
            # Per date_categorical, verificare se esiste una risposta salvata (deve essere un dizionario con chiave "risposta")
            saved_cat = previous_answer["risposta"] if isinstance(previous_answer, dict) and "risposta" in previous_answer else "NESSUNA RISPOSTA"
            default_index = get_default_index(options, saved_cat)
            cat_answer = st.radio(
                label="",
                options=options,
                index=default_index,
                key=f"question_{question_id}_cat"
            )
            if cat_answer == "Sì":
                date_value = st.date_input(
                    label="Seleziona la data (GG/MM/AAAA)",
                    key=f"question_{question_id}_date"
                )
                responses[question_id] = {"risposta": cat_answer, "data": date_value.strftime("%d/%m/%Y")}
            else:
                responses[question_id] = {"risposta": cat_answer}
        else:
            responses[question_id] = st.text_input(
                label="",
                value=previous_answer if previous_answer != "" else "NESSUNA RISPOSTA",
                key=f"question_{question_id}"
            )

    if st.button("Invia le risposte"):
        save_responses(responses, "responses.json")
        st.success("Risposte salvate con successo!")

    return responses

if __name__ == "__main__":
    # Caricamento delle risposte salvate (se esistono)
    try:
        with open("responses.json", "r", encoding="utf-8") as file:
            saved_responses = json.load(file)
    except FileNotFoundError:
        saved_responses = {}

    render_questionnaire(questions, saved_responses)