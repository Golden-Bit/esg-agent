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
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())[:8]  # un ID chat casuale

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

########################################################################################################################

def get_user_session_dir(username: str, session_id: str) -> str:
    """
    Ritorna il percorso della cartella dedicata all'utente e alla specifica session_id.
    Esempio: 'mario/AB12/'
    """
    user_dir = username
    session_dir = os.path.join("USERS_DATA", user_dir, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return session_dir

def get_user_session_files_dir(username: str, session_id: str) -> str:
    """
    Ritorna il percorso in cui salvare i file caricati (PDF, docx, etc.)
    Esempio: 'mario/AB12/files/'
    """
    base_dir = get_user_session_dir(username, session_id)
    files_dir = os.path.join(base_dir, "files")
    os.makedirs(files_dir, exist_ok=True)
    return files_dir

def get_user_session_urls_dir(username: str, session_id: str) -> str:
    """
    Ritorna il percorso in cui salvare le risorse delle URL (es. HTML scaricato, etc.).
    Esempio: 'mario/AB12/urls/'
    """
    base_dir = get_user_session_dir(username, session_id)
    urls_dir = os.path.join(base_dir, "urls")
    os.makedirs(urls_dir, exist_ok=True)
    return urls_dir

def get_user_session_forms_dir(username: str, session_id: str) -> str:
    """
    Ritorna il percorso in cui salvare i JSON dei forms.
    Esempio: 'mario/AB12/forms/'
    """
    base_dir = get_user_session_dir(username, session_id)
    forms_dir = os.path.join(base_dir, "forms")
    os.makedirs(forms_dir, exist_ok=True)
    return forms_dir

def get_user_reports_dir(username: str) -> str:
    """
    Ritorna la directory dove salvare i file di report per un certo utente.
    Esempio: 'username/reports/'
    """
    base_dir = username  # cartella base per l'utente
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)  # Crea la directory se non esiste
    return reports_dir

def get_user_chats_dir(username: str) -> str:
    """
    Ritorna la directory dove salvare i file di chat per un certo utente.
    Esempio: 'username/chats/'
    """
    base_dir = username  # Puoi modificare la posizione base se vuoi
    chats_dir = os.path.join(base_dir, "chats")
    os.makedirs(chats_dir, exist_ok=True)  # Crea la directory se non esiste
    return chats_dir

def list_user_chats(username: str) -> list:
    """
    Ritorna la lista di file chat esistenti per l'utente specificato.
    Ogni file corrisponde a una chat.
    """
    chats_dir = get_user_chats_dir(username)
    all_files = os.listdir(chats_dir)
    # Filtra solo i file con estensione .json
    json_files = [f for f in all_files if f.endswith(".json")]
    # Rimuovi l'estensione .json per mostrare i nomi chat
    chat_ids = [os.path.splitext(f)[0] for f in json_files]
    return chat_ids

def load_chat_from_file(username: str, chat_id: str) -> dict:
    """
    Carica la chat (dizionario) dal file JSON corrispondente.
    Se il file non esiste, ritorna un dizionario con nome e messages vuoti.
    """
    chats_dir = get_user_chats_dir(username)
    chat_file = os.path.join(chats_dir, f"{chat_id}.json")
    if not os.path.exists(chat_file):
        return {
            "id": chat_id,
            "name": "Nuova Chat",
            "messages": []
        }
    with open(chat_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def save_chat_to_file(username: str, chat_id: str, chat_data: dict):
    """
    Salva la struttura della chat (id, name, messages) nel file JSON corrispondente.
    """
    chats_dir = get_user_chats_dir(username)
    chat_file = os.path.join(chats_dir, f"{chat_id}.json")
    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=4)


def save_form_responses_locally(username: str, session_id: str, form_data: dict, filename: str = "questionnaire.json"):
    forms_dir = get_user_session_forms_dir(username, session_id)
    file_path = os.path.join(forms_dir, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(form_data, f, ensure_ascii=False, indent=4)


def questionnaire_page():
    username = st.session_state.get("username")
    session_id = st.session_state.session_id

    # 1) Carica risposte se esiste forms/<questionnaire.json>
    if username:
        forms_dir = get_user_session_forms_dir(username, session_id)
        q_file_path = os.path.join(forms_dir, "questionnaire.json")
        if os.path.exists(q_file_path):
            # Carichiamo su st.session_state le risposte
            with open(q_file_path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
            st.session_state["questionnaire_responses"] = saved_data
        else:
            # Se non esiste, magari inizializziamo un dict vuoto (o lasciamo com’è)
            if "questionnaire_responses" not in st.session_state:
                st.session_state["questionnaire_responses"] = {}
    else:
        st.warning("Non sei loggato, i dati del questionario non potranno essere salvati/caricati.")

    # 2) Carichiamo le domande (forms.json), dopodiché popoliamo l'interfaccia
    questions_file = "forms.json"
    questions = load_questions(questions_file)

    # 3) Render del questionario
    st.session_state["questionnaire_responses"] = render_questionnaire(questions)

    # 4) Bottone di salvataggio locale
    if st.button("Salva questionario in locale"):
        if username:
            # Salvataggio
            save_form_responses_locally(username, session_id,
                                        st.session_state["questionnaire_responses"],
                                        filename="questionnaire.json")
            st.success("Questionario salvato localmente!")
        else:
            st.warning("Devi essere loggato per salvare localmente.")

def login_page():
    """
    Pagina di login che utilizza l'endpoint /login del backend per verificare le credenziali.
    """
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Username", max_chars=50, placeholder="Inserisci il tuo username")
        password = st.text_input("Password", type="password", placeholder="Inserisci la tua password")
        login_button = st.form_submit_button("Login")

        if login_button:
            try:
                # Costruisci l'URL per l'endpoint di login usando api_address
                login_url = f"https://www.bluen.ai/api4/login"
                # Invia la richiesta POST con le credenziali come JSON
                response = requests.post(login_url, json={"username": username, "password": password})
                if response.status_code == 200:
                    data = response.json()
                    if data.get("login") is True:
                        st.session_state.logged_in = True
                        st.session_state["username"] = username  # <<-- AGGIUNGI QUESTA RIGA
                        st.success("Login effettuato con successo!")
                        st.rerun()  # Ricarica la pagina per mostrare il contenuto protetto
                    else:
                        st.error("Credenziali non valide.")
                else:
                    st.error(f"Errore: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Errore durante il login: {e}")


def documents_page():
    """
    Pagina dedicata al caricamento e alla gestione dei documenti
    """
    import os
    import json
    import base64
    import uuid
    from pathlib import Path

    st.title("Gestione Documenti")

    # Recupera username e session_id dalla sessione
    username = st.session_state.get("username", None)
    session_id = st.session_state.session_id

    # 1) Chiave del widget file_uploader (per poterlo ricreare e azzerare)
    # Se non esiste ancora in session_state, la creiamo
    if "file_upload_widget_key" not in st.session_state:
        st.session_state.file_upload_widget_key = "file_upload_main"

    # --------------------------------------- #
    # SEZIONE: Upload Documents
    # --------------------------------------- #
    st.header("Upload Documents")

    # Widget file_uploader con la chiave (variabile) in session_state
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'txt', 'docx'],
        accept_multiple_files=True,
        key=st.session_state.file_upload_widget_key
    )

    if st.button("Upload and Process Documents", use_container_width=True):
        if not session_id:
            st.error("Please enter a Session ID.")
        elif not uploaded_files:
            st.error("Please upload at least one file.")
        else:
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                file_id = uploaded_file.name.split(".")[0]
                description = f"Document uploaded: {file_id}"

                with st.spinner(f"Uploading and processing the document {file_id}..."):
                    # 1) Leggi il contenuto del file in memoria
                    file_bytes = uploaded_file.read()

                    # 2) Se l'utente è loggato, salviamo localmente
                    if username:
                        local_files_dir = get_user_session_files_dir(username, session_id)
                        local_file_path = os.path.join(local_files_dir, uploaded_file.name)

                        # Salva fisicamente il file in locale
                        with open(local_file_path, "wb") as f:
                            f.write(file_bytes)
                    else:
                        local_file_path = None
                        st.warning("Non sei loggato, il file non verrà salvato in locale.")

                    # 3) Preparazione parametri POST
                    data = {
                        'session_id': session_id,
                        'file_id': file_id,
                        'description': description,
                    }
                    upload_document_url = f"https://www.bluen.ai/api4/upload_document"

                    # 4) Prepara il file per la POST
                    if local_file_path and os.path.exists(local_file_path):
                        # Riapriamo il file salvato in locale
                        files = {
                            'uploaded_file': (uploaded_file.name, open(local_file_path, "rb")),
                        }
                    else:
                        # Altrimenti usiamo i bytes in memoria
                        files = {
                            'uploaded_file': (uploaded_file.name, file_bytes),
                        }

                    # 5) Invio la richiesta al backend
                    try:
                        response = requests.post(upload_document_url, data=data, files=files)
                        if response.status_code == 200:
                            st.success(f"Document {file_id} uploaded and processed successfully.")
                            print(f"Upload and process response for {file_id}:", response.json())
                        else:
                            st.error(f"Failed to upload document {file_id}: {response.text}")
                            print(f"Failed to upload document {file_id}: {response.status_code}, {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                        print(f"An error occurred during upload for {file_id}: {e}")

            # 6) Configurazione e caricamento della chain
            with st.spinner("Configuring and loading the agent for all documents..."):
                configure_chain_url = f"https://www.bluen.ai/api4/configure_and_load_chain/?session_id={session_id}"
                try:
                    response = requests.post(configure_chain_url)
                    if response.status_code == 200:
                        st.success("Agent configured and loaded successfully.")
                        print("Configure agent response:", response.json())
                    else:
                        st.error(f"Failed to configure agent: {response.text}")
                        print(f"Failed to configure agent: {response.status_code}, {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    print(f"An error occurred during agent configuration: {e}")

        # Al termine di TUTTI gli upload, cambiamo la chiave del widget → svuotiamo la lista
        st.session_state.file_upload_widget_key = "file_upload_" + str(uuid.uuid4())[:6]
        st.rerun()

    # --------------------------------------- #
    # MOSTRA FILE CARICATI LOCALMENTE (con card + link download)
    # --------------------------------------- #
    st.markdown("---")
    if username:
        files_dir = get_user_session_files_dir(username, session_id)
        st.subheader("File caricati localmente (per questa sessione)")

        if os.path.exists(files_dir):
            local_files = sorted(Path(files_dir).glob("*.*"))
            if local_files:
                # Contenitore scrollabile
                st.markdown("<div style='max-height:300px; overflow-y:auto;'>", unsafe_allow_html=True)

                for local_file_path in local_files:
                    file_name = local_file_path.name

                    # Creiamo un link testuale cliccabile per il download
                    with open(local_file_path, "rb") as f:
                        file_data = f.read()
                    b64_file = base64.b64encode(file_data).decode()
                    download_link = f'<a href="data:application/octet-stream;base64,{b64_file}" download="{file_name}">Clicca per scaricare</a>'

                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <strong>{file_name}</strong><br>
                        {download_link}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Nessun file presente nella cartella locale.")
        else:
            st.info("La cartella files per questa sessione non esiste ancora.")
    else:
        st.warning("Effettua il login per visualizzare i file caricati localmente.")

    # --------------------------------------- #
    # SEZIONE: Add URLs with Descriptions
    # --------------------------------------- #
    st.markdown("---")
    st.header("Add URLs with Descriptions")

    # Per la singola form di URL
    if "new_url_value" not in st.session_state:
        st.session_state.new_url_value = ""

    if "new_url_desc" not in st.session_state:
        st.session_state.new_url_desc = ""

    # Input e text_area unici
    st.session_state.new_url_value = st.text_input("URL", value=st.session_state.new_url_value, key="url_unique")
    st.session_state.new_url_desc = st.text_area("Description", value=st.session_state.new_url_desc, key="desc_unique")

    # Pulsante di salvataggio
    if st.button("Salva URL", key="save_single_url_button", use_container_width=True):
        # Verifichiamo che non siano vuoti
        if st.session_state.new_url_value.strip() and st.session_state.new_url_desc.strip():
            # Salviamo nel file
            if username:
                urls_dir = get_user_session_urls_dir(username, session_id)
                urls_file_path = os.path.join(urls_dir, "urls_list.json")

                # Leggiamo la lista esistente (se c'è)
                if os.path.exists(urls_file_path):
                    with open(urls_file_path, "r", encoding="utf-8") as f:
                        saved_urls = json.load(f)
                else:
                    saved_urls = []

                # Append la nuova URL
                saved_urls.append({
                    "url": st.session_state.new_url_value,
                    "description": st.session_state.new_url_desc
                })

                # Riscriviamo
                with open(urls_file_path, "w", encoding="utf-8") as f:
                    json.dump(saved_urls, f, ensure_ascii=False, indent=4)

                st.success("URL salvata con successo!")

                # Reset campi input
                st.session_state.new_url_value = ""
                st.session_state.new_url_desc = ""
                st.rerun()
            else:
                st.warning("Devi essere loggato per salvare localmente.")
        else:
            st.warning("Compila sia URL che Description.")

    # MOSTRA GLI URL SALVATI LOCALMENTE (card style, in contenitore scrollabile)
    if username:
        urls_dir = get_user_session_urls_dir(username, session_id)
        urls_file_path = os.path.join(urls_dir, "urls_list.json")
        if os.path.exists(urls_file_path):
            with open(urls_file_path, "r", encoding="utf-8") as f:
                saved_urls = json.load(f)

            st.subheader("URL salvati localmente (per questa sessione)")
            if saved_urls:
                # Contenitore scrollabile
                st.markdown("<div style='max-height:300px; overflow-y:auto;'>", unsafe_allow_html=True)

                for i, item in enumerate(saved_urls, start=1):
                    url_val = item["url"]
                    desc = item["description"]
                    st.markdown(f"""
                    <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
                        <strong>URL #{i}</strong><br>
                        <em>Link:</em> <a href="{url_val}" target="_blank">{url_val}</a><br>
                        <em>Descrizione:</em> {desc}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Non ci sono URL salvati.")
        else:
            st.info("Nessun file urls_list.json trovato nella cartella locale.")
    else:
        st.warning("Effettua il login per visualizzare gli URL salvati.")


def reports_page():
    st.title("I tuoi Report")

    username = st.session_state.get("username", None)
    if not username:
        st.error("Non sei loggato, impossibile visualizzare i report.")
        return

    # Ottieni la cartella dei report dell'utente
    reports_dir = get_user_reports_dir(username)

    if not os.path.exists(reports_dir):
        st.write("Non ci sono report disponibili.")
        return

    files = os.listdir(reports_dir)
    docx_files = [f for f in files if f.endswith(".docx")]

    if not docx_files:
        st.write("Non ci sono report disponibili.")
        return

    st.write("Seleziona un report per scaricarlo:")
    for file in docx_files:
        file_path = os.path.join(reports_dir, file)
        # Forniamo un pulsante di download
        with open(file_path, "rb") as f:
            st.download_button(
                label=f"Scarica {file}",
                data=f.read(),
                file_name=file,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=file
            )

########################################
# Funzioni di utilità per API Keys
########################################

def load_api_keys(filename="api_keys.json"):
    """
    Carica l'elenco delle chiavi API da un file JSON.
    Se il file non esiste o è vuoto, restituisce una lista vuota.
    """
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get("openai_api_keys", [])
        except json.JSONDecodeError:
            return []

def save_api_keys(api_keys, filename="api_keys.json"):
    """
    Salva l'elenco delle chiavi API in un file JSON.
    """
    data = {"openai_api_keys": api_keys}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generate_key_id():
    """
    Genera un ID univoco (brevi) per identificare ogni chiave.
    """
    return str(uuid.uuid4())[:8]

########################################
# Esempio di modifica al dashboard_page
########################################

def dashboard_page():
    st.title("Dashboard Admin")

    # ---------------------------- #
    # Sezione: Creazione Nuovo Utente
    # ---------------------------- #
    st.subheader("Crea Nuovo Utente")
    with st.form("create_user_form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        submit_new_user = st.form_submit_button("Crea Utente")
        if submit_new_user:
            register_url = f"https://www.bluen.ai/api4/register"
            response = requests.post(register_url, json={"username": new_username, "password": new_password})
            if response.status_code == 200:
                st.success("Utente creato con successo!")
            else:
                st.error(f"Errore: {response.status_code} - {response.text}")

    # ---------------------------- #
    # Sezione: Cambia Password Utente
    # ---------------------------- #
    st.subheader("Cambia Password Utente")
    with st.form("change_password_form"):
        target_username = st.text_input("Username Utente da modificare")
        new_password_for_user = st.text_input("Nuova Password", type="password")
        submit_change = st.form_submit_button("Cambia Password")
        if submit_change:
            reset_url = f"{api_address}/reset_password"
            payload = {
                "requestor_username": "admin",
                "requestor_password": "admin",  # Credenziali admin hardcoded
                "target_username": target_username,
                "new_password": new_password_for_user
            }
            response = requests.post(reset_url, json=payload)
            if response.status_code == 200:
                st.success("Password cambiata con successo!")
            else:
                st.error(f"Errore: {response.status_code} - {response.text}")

    st.subheader("Lista Utenti")
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
        for username, hashed_password in users.items():
            # Password oscurata
            obfuscated = "********"
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:10px;">
                    <strong>Username:</strong> {username}<br>
                    <strong>Password:</strong> {obfuscated}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Elimina", key=f"delete_{username}"):
                    delete_url = f"{api_address}/delete_user"
                    payload = {
                        "requestor_username": "admin",
                        "requestor_password": "admin",
                        "target_username": username
                    }
                    response = requests.delete(delete_url, json=payload)
                    if response.status_code == 200:
                        st.success(f"Utente {username} eliminato.")
                        st.rerun()
                    else:
                        st.error(f"Errore: {response.status_code} - {response.text}")
    else:
        st.write("Nessun utente registrato.")

    # ---------------------------- #
    # SEZIONE: Gestione Chiavi OpenAI
    # ---------------------------- #
    st.subheader("Gestione Chiavi OpenAI")

    # Carica le chiavi esistenti dal file
    api_keys = load_api_keys()

    # Inizializza (se non esiste) lo stato per mostrare/nascondere le chiavi
    if "show_api_keys" not in st.session_state:
        st.session_state["show_api_keys"] = False

    # Form per aggiungere una nuova chiave
    with st.form("add_api_key_form"):
        new_api_key = st.text_input("Inserisci nuova API Key OpenAI", type="password")
        add_key_btn = st.form_submit_button("Aggiungi Chiave")
        if add_key_btn and new_api_key.strip():
            # Crea un record con ID e chiave
            new_record = {
                "id": generate_key_id(),
                "key": new_api_key.strip()
            }
            api_keys.append(new_record)
            save_api_keys(api_keys)
            st.success("Nuova API Key aggiunta con successo!")
            st.rerun()

    # Bottone toggle: mostra/nascondi chiavi
    if st.button("Mostra/Nascondi Chiavi"):
        st.session_state["show_api_keys"] = not st.session_state["show_api_keys"]

    # Se ci sono chiavi, visualizzale (mascherate o in chiaro)
    if api_keys:
        st.markdown("#### Chiavi API esistenti:")
        for record in api_keys:
            key_id = record["id"]
            key_value = record["key"]

            colA, colB, colC = st.columns([1.2, 3, 1])
            with colA:
                st.markdown(f"**ID:** `{key_id}`")
            with colB:
                if st.session_state["show_api_keys"]:
                    # Mostra la chiave in chiaro
                    st.markdown(f"**Key:** `{key_value}`")
                else:
                    # Oscura la chiave (es. sostituisce tutti i caratteri con asterischi)
                    masked = "•" * len(key_value)
                    st.markdown(f"**Key:** `{masked}`")
            with colC:
                # Pulsante di rimozione
                if st.button("Rimuovi", key=f"remove_{key_id}"):
                    # Rimuovi la chiave dall'elenco
                    api_keys = [k for k in api_keys if k["id"] != key_id]
                    save_api_keys(api_keys)
                    st.success(f"Chiave con ID {key_id} rimossa.")
                    st.rerun()
    else:
        st.markdown("*Nessuna chiave API salvata.*")


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
    session_id = st.session_state.session_id
    st.sidebar.header("Report")

    if st.sidebar.button("Download Report", use_container_width=True):
        download_report()

    if st.sidebar.button("Genera Report", use_container_width=True):
        if session_id:
            st.sidebar.success("Generazione report in corso...")
            generate_report(session_id)
        else:
            st.sidebar.error("Per favore, inserisci un Session ID valido.")
    st.sidebar.markdown("---")

    st.sidebar.markdown(
        """
        <style>
        /* Contenitore con altezza fissa e scroll verticale */
        .fixed-height-chats {
            max-height: 250px; /* o l'altezza che preferisci */
            overflow-y: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Sidebar for file upload and chain configuration
    #st.sidebar.header("Upload Documents")
    if st.session_state.logged_in:
        st.sidebar.subheader("Le tue chat esistenti")

        # 1) Pulsante "Crea Chat" con simbolo "+"
        if st.sidebar.button("➕ Crea Chat", use_container_width=True, key="new_chat_button"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state.chat_id = new_id
            st.session_state.chat_name = "Nuova Chat"  # Nome di default
            st.session_state.messages = copy.deepcopy(chatbot_config["messages"])
            st.session_state.chat_history = copy.deepcopy(chatbot_config["messages"])
            st.rerun()

        # 2) Elenco chat in contenitore scrollabile
        user_chats_ids = list_user_chats(st.session_state["username"])

        # Avvolgi i pulsanti chat in un DIV con la classe "fixed-height-chats"
        st.sidebar.markdown("<div class='fixed-height-chats'>", unsafe_allow_html=True)

        for c_id in user_chats_ids:
            # Carica i dati per recuperare il nome
            tmp_data = load_chat_from_file(st.session_state["username"], c_id)
            chat_name = tmp_data["name"]

            # Pulsante con larghezza piena
            if st.sidebar.button(chat_name, use_container_width=True, key=f"load_chat_{c_id}"):
                st.session_state.chat_id = c_id
                st.session_state.chat_name = tmp_data["name"]
                st.session_state.messages = tmp_data["messages"]
                st.session_state.chat_history = copy.deepcopy(tmp_data["messages"])
                st.rerun()

        # Chiudi il DIV scrollabile
        st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # Sidebar: Add "Genera Report" button at the top
    #st.sidebar.header("Actions")
    #session_id = st.sidebar.text_input("Session ID", value="", placeholder="Inserisci Session ID")
    session_id = st.session_state.session_id
    # Sidebar for file upload and chain configuration

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

    if "username" in st.session_state and "chat_id" in st.session_state and "chat_name" in st.session_state:
        chat_data = {
            "id": st.session_state.chat_id,
            "name": st.session_state.chat_name,
            "messages": st.session_state.messages
        }
        save_chat_to_file(st.session_state["username"], st.session_state.chat_id, chat_data)

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

    # AL TERMINE: salvataggio automatico del docx
    username = st.session_state.get("username")
    if username and st.session_state.current_html_address:
        html_content = scarica_html(st.session_state.current_html_address)
        if html_content:
            docx_file_path = "final_report.docx"  # Nome di base, volendo puoi usare un timestamp
            docx_file = converti_html_in_docx(html_content, docx_file_path)

            # Ottieni la directory dell'utente per i report
            user_reports_dir = get_user_reports_dir(username)

            # Scegli un nome univoco (puoi usare un timestamp, un uuid, ecc.)
            unique_filename = f"report_{uuid.uuid4().hex[:8]}.docx"
            full_save_path = os.path.join(user_reports_dir, unique_filename)

            # Salva effettivamente il file nella cartella utente
            if docx_file:
                # docx_file qui è "report.docx" già scritto su disco,
                # se la tua funzione `converti_html_in_docx` crea un file fisico.
                # In caso tu stia restituendo `bytes`, cambia di conseguenza.
                if os.path.exists(docx_file):
                    os.rename(docx_file, full_save_path)
                else:
                    # Se converti_html_in_docx restituisce bytes, gestisci così:
                    # with open(full_save_path, "wb") as f:
                    #     f.write(docx_file)
                    pass

                st.success(f"Report generato e salvato come: {full_save_path}")
            else:
                st.error("Impossibile convertire il contenuto HTML in DOCX.")
        else:
            st.error("Impossibile scaricare l'HTML dall'indirizzo corrente.")
    else:
        st.error("Report non generato o utente non loggato.")

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

        if st.button("Documents", key="documents_button", use_container_width=True):
            st.session_state["current_page"] = "documents"

        if st.sidebar.button("Reports", key="reports_button", use_container_width=True):
            st.session_state["current_page"] = "reports"

        # Se l'utente loggato è admin, mostra il bottone per la Dashboard
        if st.session_state.get("username") == "admin":
            if st.sidebar.button("Dashboard", key="dashboard_button", use_container_width=True):
                st.session_state["current_page"] = "dashboard"

    st.sidebar.markdown("---")

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
    elif st.session_state.get("current_page") == "dashboard":  # <<-- AGGIUNGI QUESTA CONDIZIONE
        dashboard_page()
    elif st.session_state.get("current_page") == "documents":
        documents_page()
    elif st.session_state.get("current_page") == "reports":
        reports_page()

# Se l'utente non è loggato, mostra la login_page
if not st.session_state.logged_in:
    login_page()
else:
    # Se loggato, richiama main()
    main()
