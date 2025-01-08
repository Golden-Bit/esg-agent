import json
import os
import base64
import uuid
from typing import Any
import requests
import streamlit as st
import copy
import re
from docx import Document
from html2docx import html2docx

from scope3_form import render_scope3_form
from scope1_form import render_scope1_form
from scope2_form import render_scope2_form
from forms_ui import render_questionnaire, load_questions
from utilities import graph_notes_2, graph_notes_1_5, graph_notes_3_1, graph_notes_4_1, graph_notes_ESRS_index
from utilities import linee_guida_intro, linee_guida_1_1, linee_guida_1_2, linee_guida_1_3, linee_guida_2, linee_guida_3, linee_guida_1_4, linee_guida_1_5, linee_guida_2_1, linee_guida_2_2, linee_guida_2_3, linee_guida_2_4, linee_guida_2_5, linee_guida_2_6, linee_guida_3_1, linee_guida_4_1, linee_guida_conclusione, linee_guida_4, linee_guida_info_contatto, linee_guida_nota_motedologica, linee_guida_3_2, linee_guida_3_3, linee_guida_4_2, linee_guida_4_3, linee_guida_indice_esrs
from config import chatbot_config

########################################################################################################################

api_address = chatbot_config["api_address"]

########################################################################################################################

st.set_page_config(page_title=chatbot_config["page_title"],
                   page_icon=chatbot_config["page_icon"],
                   layout="wide",
                   initial_sidebar_state="auto",
                   menu_items=None)

if "messages" not in st.session_state:
    st.session_state.messages = copy.deepcopy(chatbot_config["messages"])

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:6]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = copy.deepcopy(chatbot_config["messages"])

if "ai_avatar_url" not in st.session_state:
    st.session_state.ai_avatar_url = chatbot_config["ai_avatar_url"]

if "user_avatar_url" not in st.session_state:
    st.session_state.user_avatar_url = chatbot_config["user_avatar_url"]

if "current_html_address" not in st.session_state:
    st.session_state.current_html_address = None


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

########################################################################################################################

def questionnaire_page():
    """
    Funzione per mostrare la pagina del questionario.
    """
    #st.title("Questionario ESG")
    #st.markdown("Completa il questionario seguente.")

    # Renderizza il questionario e salva le risposte nella variabile di sessione
    if "questionnaire_responses" not in st.session_state:
        st.session_state["questionnaire_responses"] = {}  # Inizializza risposte vuote

    questions_file = "forms.json"
    questions = load_questions(questions_file)

    st.session_state["questionnaire_responses"] = render_questionnaire(questions)  # Usa render_quest()

    # Pulsante per salvare e tornare al chatbot
    #if st.button("Salva e torna al chatbot"):
    #    # Salva le risposte su file
    #    with open("responses.json", "w", encoding="utf-8") as f:
    #        json.dump(st.session_state["questionnaire_responses"], f, ensure_ascii=False, indent=4)

    #    st.session_state["current_page"] = "chatbot"  # Cambia pagina al chatbot
    #    st.rerun()  # Ricarica la pagina per riflettere il cambio di stato

def login_page():
    """
    Pagina di login con un form, input ridotti in larghezza e un pulsante di login a larghezza completa.
    """
    st.title("Login")

    # Utilizzo di un form per strutturare il layout
    with st.form("login_form"):
        # Input per username e password con larghezza personalizzata
        username = st.text_input("Username", max_chars=50, placeholder="Inserisci il tuo username")
        password = st.text_input("Password", type="password", placeholder="Inserisci la tua password")

        # Pulsante di login a larghezza completa
        login_button = st.form_submit_button("Login")

        if login_button:
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.success("Login effettuato con successo!")
                st.rerun()  # Ricarica la pagina
            else:
                st.error("Credenziali non valide.")


def download_json_file(data: dict, filename: str):
    """Converts a dictionary into a downloadable JSON file."""
    json_data = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{filename}">Scarica {filename}</a>'
    return href

def is_complete_utf8(data: bytes) -> bool:
    """Verifica se `data` rappresenta una sequenza UTF-8 completa."""
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False

def aggiorna_html_address(message):
    import re
    # Cerca un indirizzo che inizia con http://, contiene numeri e lettere, e termina con .html
    match = re.search(r'http://[\d\.\w\:/-]+\.html', message)
    if match:
        st.session_state.current_html_address = match.group()

    print(st.session_state.current_html_address)

def scarica_html(url):
    """Scarica il contenuto HTML da un URL."""
    try:
        risposta = requests.get(url)
        if risposta.status_code == 200:
            return risposta.text
        else:
            st.error(f"Errore nel download dell'HTML: {risposta.status_code}")
            return None
    except Exception as e:
        st.error(f"Errore durante il download dell'HTML: {e}")
        return None


def converti_html_in_docx_(html_content, output_path):
    template_path = "Carta_intestata_Bluen.docx"

    """
    Converte l'HTML in contenuto DOCX e lo aggiunge a un documento esistente con carta intestata.

    Args:
        html_content (str): Contenuto HTML da convertire.
        template_path (str): Percorso del documento DOCX esistente con carta intestata.
        output_path (str): Percorso in cui salvare il documento aggiornato.
    """
    try:
        pattern = r"<head>.*?</head>"

        # Rimuove il blocco <head> dal contenuto HTML
        html_content = re.sub(pattern, "", html_content, flags=re.DOTALL)
        # Converti l'HTML in un oggetto BytesIO
        docx_io = html2docx(html_content, title="out_doc")

        # Crea un nuovo documento Word dal contenuto convertito
        temp_doc = Document(docx_io)

        # Apri il documento DOCX esistente con carta intestata
        template_doc = Document(template_path)

        # Aggiungi il contenuto HTML convertito al documento esistente
        for element in temp_doc.element.body:
            template_doc.element.body.append(element)

        # Salva il documento aggiornato con il contenuto HTML
        template_doc.save(output_path)
        print(f"Documento salvato con successo in: {output_path}")
    except Exception as e:
        print(f"Errore durante la conversione o l'inserimento: {e}")

    return output_path

def converti_html_in_docx(html_content, output_file=None):
    """
    Converte l'HTML in un file DOCX, eliminando esattamente il blocco <head>.
    """
    try:
        # Definisci una regex per catturare il blocco <head>... </head>
        pattern = r"<head>.*?</head>"

        # Rimuove il blocco <head> dal contenuto HTML
        html_content = re.sub(pattern, "", html_content, flags=re.DOTALL)

        # Converti l'HTML in DOCX
        docx_file = html2docx(title="Document from HTML", content=html_content)

        # Se un file di output è specificato, salvalo
        if output_file:
            with open(output_file, "wb") as f:
                f.write(docx_file.getvalue())
            return output_file

        # Altrimenti, restituisci il contenuto DOCX come bytes
        return docx_file.getvalue()
    except Exception as e:
        st.error(f"Errore durante la conversione in DOCX: {e}")
        return None

def converti_html_in_docx__(html_content, output_path):
    template_path = "Carta_intestata_Bluen.docx"

    """
    Converte l'HTML in contenuto DOCX e lo aggiunge a un documento già esistente con carta intestata.

    Args:
        html_content (str): Contenuto HTML da convertire.
        template_path (str): Percorso del documento DOCX esistente con carta intestata.
        output_path (str): Percorso in cui salvare il documento aggiornato.
    """
    try:
        # Rimuovi il blocco <head> dal contenuto HTML
        pattern = r"<head>.*?</head>"
        html_content = re.sub(pattern, "", html_content, flags=re.DOTALL)

        # Converti l'HTML in un contenuto DOCX (come bytes)
        docx_content = html2docx(title="Document from HTML", content=html_content).getvalue()

        # Apri il documento DOCX esistente con carta intestata
        template_doc = Document(template_path)

        # Crea un documento temporaneo per il contenuto HTML convertito
        temp_doc_path = "temp_doc.docx"
        with open(temp_doc_path, "wb") as temp_file:
            temp_file.write(docx_content)
        temp_doc = Document(temp_doc_path)

        # Mappa gli stili di 'temp_doc' per preservare formattazioni personalizzate
        for style in temp_doc.styles:
            if style not in template_doc.styles:
                template_doc.styles.add_style(style.name, style.type)

        # Aggiungi il contenuto HTML convertito al documento esistente
        for element in temp_doc.element.body:
            # Preserva immagini e stili personalizzati
            template_doc.element.body.append(element)

        # Salva il documento aggiornato con il contenuto HTML
        template_doc.save(output_path)
        print(f"Documento salvato con successo in: {output_path}")

        # Rimuovi il file temporaneo
        if os.path.exists(temp_doc_path):
            os.remove(temp_doc_path)

    except Exception as e:
        print(f"Errore durante la conversione o l'inserimento: {e}")

    return output_path

def download_report():
    if st.session_state.current_html_address:
        html_content = scarica_html(st.session_state.current_html_address)
        if html_content:
            docx_file = converti_html_in_docx(html_content, "report.docx")
            if docx_file:
                with open(docx_file, "rb") as f:
                    st.download_button(
                        label="Scarica il report DOCX",
                        data=f,
                        file_name="report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
        else:
            st.error("Impossibile scaricare l'HTML dall'indirizzo fornito.")
    else:
        st.error("Nessun indirizzo HTML corrente trovato.")


def chatbot_page():

    # Sidebar for file upload and chain configuration
    #st.sidebar.header("Upload Documents")

    # Sidebar: Add "Genera Report" button at the top
    #st.sidebar.header("Actions")
    #session_id = st.sidebar.text_input("Session ID", value="", placeholder="Inserisci Session ID")
    session_id = st.session_state.session_id
    # Sidebar for file upload and chain configuration
    st.sidebar.header("Upload Documents")
    #session_id = st.sidebar.text_input("Session ID")
    uploaded_files = st.sidebar.file_uploader("Choose files", type=['pdf', 'txt', 'docx'], accept_multiple_files=True)

    if st.sidebar.button("Upload and Process Documents", use_container_width=True):
        if not session_id:
            st.sidebar.error("Please enter a Session ID.")
        elif not uploaded_files:
            st.sidebar.error("Please upload at least one file.")
        else:
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                file_id = uploaded_file.name.split(".")[0]
                description = f"Document uploaded: {file_id}"

                with st.spinner(f"Uploading and processing the document {file_id}..."):
                    # Prepare the data
                    files = {
                        'uploaded_file': (uploaded_file.name, uploaded_file.read()),
                    }
                    data = {
                        'session_id': session_id,
                        'file_id': file_id,
                        'description': description,
                    }

                    upload_document_url = f"http://127.0.0.1:8100/upload_document"

                    try:
                        response = requests.post(upload_document_url, data=data, files=files)
                        if response.status_code == 200:
                            st.sidebar.success(f"Document {file_id} uploaded and processed successfully.")
                            print(f"Upload and process response for {file_id}:", response.json())
                        else:
                            st.sidebar.error(f"Failed to upload document {file_id}: {response.text}")
                            print(f"Failed to upload document {file_id}: {response.status_code}, {response.text}")
                    except Exception as e:
                        st.sidebar.error(f"An error occurred: {e}")
                        print(f"An error occurred during upload for {file_id}: {e}")

            # Configure a single agent for all documents
            with st.spinner("Configuring and loading the agent for all documents..."):
                configure_chain_url = f"http://127.0.0.1:8100/configure_and_load_chain/?session_id={session_id}"
                try:
                    response = requests.post(configure_chain_url)
                    if response.status_code == 200:
                        st.sidebar.success("Agent configured and loaded successfully.")
                        print("Configure agent response:", response.json())
                    else:
                        st.sidebar.error(f"Failed to configure agent: {response.text}")
                        print(f"Failed to configure agent: {response.status_code}, {response.text}")
                except Exception as e:
                    st.sidebar.error(f"An error occurred: {e}")
                    print(f"An error occurred during agent configuration: {e}")

    st.sidebar.markdown("---")

    # Section for adding multiple URLs with descriptions
    st.sidebar.header("Add URLs with Descriptions")

    if "url_forms" not in st.session_state:
        st.session_state.url_forms = [{"url": "", "description": ""}]

    if st.sidebar.button("+ Add New URL Form", use_container_width=True):
        st.session_state.url_forms.append({"url": "", "description": ""})

    # Display all URL forms
    for idx, form in enumerate(st.session_state.url_forms):
        #st.sidebar.markdown(f"#### URL Form {idx + 1}")
        form["url"] = st.sidebar.text_input(f"URL {idx + 1}", value=form["url"], key=f"url_{idx}")
        form["description"] = st.sidebar.text_area(f"Description {idx + 1}", value=form["description"],
                                                   key=f"description_{idx}")

    # Save all URLs at once with a single button
    if st.sidebar.button("Save All URLs", use_container_width=True):
        if all(form["url"] and form["description"] for form in st.session_state.url_forms):
            st.sidebar.success("All URLs and descriptions saved successfully.")
        else:
            st.sidebar.error("Please ensure all URL forms are filled out completely.")
    st.sidebar.markdown("---")



    # Main chat interface
    previus_type = None
    for message in st.session_state.messages:

        if message["role"] == "user" and previus_type != "user":
            with st.chat_message(message["role"], avatar=st.session_state.user_avatar_url):
                st.markdown(message["content"])
        elif message["role"] != "user":
            with st.chat_message(message["role"], avatar=st.session_state.ai_avatar_url):
                st.markdown(message["content"])
        previus_type = message["role"]
    if prompt := st.chat_input("Scrivi qualcosa"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        generate_response(prompt, session_id)

    st.sidebar.header("Report")

    if st.sidebar.button("Download Report", use_container_width=True):
        download_report()

    if st.sidebar.button("Genera Report", use_container_width=True):
        if session_id:
            st.sidebar.success("Generazione report in corso...")
            generate_report(session_id)
        else:
            st.sidebar.error("Per favore, inserisci un Session ID valido.")


    st.sidebar.markdown(
        """
        <div style="text-align: center; margin-top: 20px; font-size: 12px; color: black;">
            &copy; 2024 Bluen s.r.l. Tutti i diritti riservati.
        </div>
        """,
        unsafe_allow_html=True
    )

def generate_response(prompt, session_id, auto_generated=False):
    """Handles generating a response based on a prompt."""
    chain_id = f"{session_id}-workflow_generation_chain"
    input_suffix = f"""*NOTE IMPORTANTI:* 
    - Preleva informazioni utili dai vector stores, dai file in locale e dai seguenti URLs se necessario: {json.dumps(st.session_state.url_forms, indent=2) if st.session_state.url_forms else "[urls assenti]"}
    - non devi necessariamente fare grafici in qualuqnue circostanza, evita i grafici inutili e poco professionali, cioè che potrebberoe ssere trnaquillamente spiegati a parole o in tabella. focalizzati sui grafici richeisti.
    - quando generi grafici stai molto attentoa  usare etichette sintetiche per evitare che si sovrapponghino, oppure usa ad esempio colori con leggenda nei grafici a barre e altri tipi di grafici in cui nomi lunghi delle etichette deid ati su gli assi potrebbero sovrapporsi."""

    # Show the user message in the chat only if it's not auto-generated
    if not auto_generated:
        with st.chat_message("user", avatar=st.session_state.user_avatar_url):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

    if auto_generated:
        st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=st.session_state.ai_avatar_url):
        message_placeholder = st.empty()
        s = requests.Session()
        full_response = ""
        url = f"{api_address}/chains/stream_events_chain"
        payload = {
            "chain_id": chain_id,
            "query": {
                "input": f"{prompt}\n{input_suffix}",
                "chat_history": st.session_state.chat_history[-6:] if len(st.session_state.chat_history) > 6
                else st.session_state.chat_history
            },
            "inference_kwargs": {},
        }

        non_decoded_chunk = b''
        with s.post(url, json=payload, headers=None, stream=True) as resp:
            for chunk in resp.iter_content():
                if chunk:
                    non_decoded_chunk += chunk
                    if is_complete_utf8(non_decoded_chunk):
                        decoded_chunk = non_decoded_chunk.decode("utf-8")
                        full_response += decoded_chunk
                        message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                        non_decoded_chunk = b''  # Clear buffer

        message_placeholder.markdown(full_response)

    # Add assistant's response to chat history if not auto-generated
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    aggiorna_html_address(full_response)
def generate_report(session_id):
    """Generates a report with predefined messages."""
    report_messages = [
    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Evita termini come 'benvenuti al' o 'nel nostro dna' etc..  Sviluppa contenuto sezione 'introduzione' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_intro}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'introduzione' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave 'Introduzione' e contenuti adatti in formato html",


    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 1.1 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_1}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli! Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli! Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.1 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 1.2 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_2}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.2 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 1.3 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_3}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.3 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 1.4 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_4}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.4 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 1.5 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_5}. {graph_notes_1_5}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.5 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",


    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto 'Descrizione Cap. 2' (nel prossimo messaggio ti chieiderò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2}. {graph_notes_2}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Descrizione Cap. 2' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 2.1 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede .{linee_guida_2_1} .{graph_notes_2}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.1 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 2.2 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_2}.{graph_notes_2}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.2 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 2.3 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_3}.{graph_notes_2}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.3 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 2.4 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_4}.{graph_notes_2}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.4 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 2.5 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_5}.{graph_notes_2}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.5 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 2.6 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_6}.{graph_notes_2}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.6 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",


    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto 'Descrizione Cap. 3' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_3}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Descrizione Cap. 3' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 3.1 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_3_1}.{graph_notes_3_1}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 3.1 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 3.2 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_3_2}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 3.2 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 3.3 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_3_3}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 3.3 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",


    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto 'Descrizione Cap. 4' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_4}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Descrizione Cap. 4' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 4.1 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede.{linee_guida_4_1}. {graph_notes_4_1}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 4.1 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 4.2 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_4_2}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 4.2 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 4.3 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_4_3}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 4.3 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",


    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!   contenuto sezione 'Conclusione' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_conclusione}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Conclusione' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 'Nota metodologica' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_nota_motedologica}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Nota metodologica' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 'Indice ESRS' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_indice_esrs}. {graph_notes_ESRS_index}",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Indice ESRS' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Sviluppa contenuto sezione 'Informazioni di contatto' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_info_contatto}.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Il contenuto che svilupperai dovrà avere un stilo infromale e professionale, inoltre riporta solo dati e informazioni che abbiano un aspetto serio e un senso di essere mostrate usando grafici complessi.Evita termini come 'benvenuti al' o 'nel nostro dna' etc.. Evita frasi del tipo 'Non sono riuscito a ottenere informazioni dettagliate dai vector stores' (non fare riferimento a vector store)... Inoltre cosa importantissima, assicurati di generare solo i grafici e le tabelle coerenti con l attuale sezione, ed evita la rindondanza di grafici identici ripetutti più volte! Inoltre se la sezione non richeide grafici allora non generarli!  Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Informazioni di contatto' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",
]



    for message in report_messages:
        # Use auto_generated=True to avoid duplicating messages in chat history
        generate_response(message, session_id, auto_generated=True)

########################################################################################################################

def main():
    """
    Gestisce la logica principale dell'app Streamlit.
    """
    # Sidebar per la navigazione tra Chatbot e Questionario

    #col1, col2 = st.sidebar.columns(2)

    st.sidebar.markdown(
        """
        <div style="text-align: center;">
            <img src="https://static.wixstatic.com/media/63b1fb_6c4848f63b21475db8775af35ee50e55~mv2.png" alt="Logo" style="width: 300px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("---")

    st.sidebar.header("Pages")

    with st.sidebar:
        if st.button("Bluen AI", key="chatbot_button", use_container_width=True):
            st.session_state["current_page"] = "chatbot"

        #with col2:
        if st.button("ESG Assessment Form", key="questionnaire_button", use_container_width=True):
            st.session_state["current_page"] = "questionnaire"

        # AGGIUNTA: bottone per la pagina Scope 2
        if st.sidebar.button("GHG Form (Scope 1)", key="scope1_button", use_container_width=True):
            st.session_state["current_page"] = "scope1"

        # AGGIUNTA: bottone per la pagina Scope 2
        if st.sidebar.button("GHG Form (Scope 2)", key="scope2_button", use_container_width=True):
            st.session_state["current_page"] = "scope2"

        # AGGIUNTA: bottone per la pagina Scope 2
        if st.sidebar.button("GHG Form (Scope 3)", key="scope3_button", use_container_width=True):
            st.session_state["current_page"] = "scope3"

    st.sidebar.markdown("---")

        # Mostra la pagina selezionata
    if st.session_state.get("current_page", "chatbot") == "chatbot":
        chatbot_page()  # Funzione che gestisce la logica del chatbot
    elif st.session_state.get("current_page") == "questionnaire":
        questionnaire_page()
    elif st.session_state.get("current_page") == "scope1":
        render_scope1_form(session_id=st.session_state.session_id)
    elif st.session_state.get("current_page") == "scope2":
        render_scope2_form(session_id=st.session_state.session_id)
    elif st.session_state.get("current_page") == "scope3":
        render_scope3_form(session_id=st.session_state.session_id)


# Se l'utente non è loggato, mostra la login_page
if not st.session_state.logged_in:
    login_page()
else:
    # Se loggato, richiama main()
    main()
