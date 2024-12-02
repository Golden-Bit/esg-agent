import json
import os
import base64
from typing import Any
import requests
import streamlit as st
import copy

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

if "chat_history" not in st.session_state:
    st.session_state.chat_history = copy.deepcopy(chatbot_config["messages"])

if "ai_avatar_url" not in st.session_state:
    st.session_state.ai_avatar_url = chatbot_config["ai_avatar_url"]

if "user_avatar_url" not in st.session_state:
    st.session_state.user_avatar_url = chatbot_config["user_avatar_url"]

########################################################################################################################
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

def main():

    # Sidebar for file upload and chain configuration
    #st.sidebar.header("Upload Documents")

    st.sidebar.markdown(
        """
        <div style="text-align: center;">
            <img src="https://static.wixstatic.com/media/63b1fb_6c4848f63b21475db8775af35ee50e55~mv2.png" alt="Logo" style="width: 300px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    # Sidebar: Add "Genera Report" button at the top
    st.sidebar.header("Actions")
    session_id = st.sidebar.text_input("Session ID", value="", placeholder="Inserisci Session ID")
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
def generate_report(session_id):
    """Generates a report with predefined messages."""
    report_messages = [
    f"Sviluppa contenuto sezione 'introduzione' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_intro}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'introduzione' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave 'Introduzione' e contenuti adatti in formato html",


    f"Sviluppa contenuto sezione 1.1 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_1}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.1 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 1.2 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_2}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.2 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 1.3 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_3}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.3 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 1.4 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_4}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.4 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 1.5 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_1_5}. {graph_notes_1_5}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 1.5 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",


    f"Sviluppa contenuto 'Descrizione Cap. 2' (nel prossimo messaggio ti chieiderò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2}. {graph_notes_2}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Descrizione Cap. 2' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 2.1 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede .{linee_guida_2_1} .{graph_notes_2}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.1 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 2.2 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_2}.{graph_notes_2}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.2 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 2.3 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_3}.{graph_notes_2}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.3 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 2.4 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_4}.{graph_notes_2}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.4 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 2.5 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_5}.{graph_notes_2}",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.5 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 2.6 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_2_6}.{graph_notes_2}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 2.6 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",


    f"Sviluppa contenuto 'Descrizione Cap. 3' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_3}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Descrizione Cap. 3' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 3.1 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_3_1}.{graph_notes_3_1}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 3.1 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 3.2 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_3_2}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 3.2 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 3.3 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_3_3}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 3.3 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",


    f"Sviluppa contenuto 'Descrizione Cap. 4' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_4}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Descrizione Cap. 4' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 4.1 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede.{linee_guida_4_1}. {graph_notes_4_1}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 4.1 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 4.2 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_4_2}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 4.2 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 4.3 (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_4_3}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 4.3 del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",


    f"Sviluppa contenuto sezione 'Conclusione' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_conclusione}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Conclusione' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 'Nota metodologica' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_nota_motedologica}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Nota metodologica' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 'Indice ESRS' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_indice_esrs}. {graph_notes_ESRS_index}",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Indice ESRS' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",

    f"Sviluppa contenuto sezione 'Informazioni di contatto' (nel prossimo messaggio ti chiederò di inserire il contenuto generato nel template html). Genera contenuton in formato html, duqnue inserisci contenuto dettagliato ed eventualmente inserisci tabelle, grafici e diagrammi quando la situazione lo richiede. {linee_guida_info_contatto}.",
    "In base al contenuto appena generato per la sezione crea e salva effettivamente i grafici richiesti, duqnue riscrivi il contenuto html inserendo i link che puntano ai grafici salvati. I grafici salvati andranno visualizzati nell html della sezione centrati orizzontalmente.",
    "Inserisci contenuto generato nel messaggio precedente all'interno della sezione 'Informazioni di contatto' del template. USA assolutamente STRUMENTO replace_placeholder_in_html fornendo in input chiave e contenuti adatti in formato html",
]



    for message in report_messages:
        # Use auto_generated=True to avoid duplicating messages in chat history
        generate_response(message, session_id, auto_generated=True)

########################################################################################################################

main()
