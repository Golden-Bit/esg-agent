import json
import os
import base64
from typing import Any
import requests
import streamlit as st
import copy
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


    # Sidebar: Add "Genera Report" button at the top
    if st.sidebar.button("Genera Report", use_container_width=True):
        st.sidebar.success("Report generato con successo!")  # Puoi sostituire questa parte con la logica effettiva per generare un report.

    # Sidebar for file upload and chain configuration
    st.sidebar.header("Upload Documents")
    session_id = st.sidebar.text_input("Session ID")
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

                    upload_document_url = f"http://34.91.209.79:800/upload_document"

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
                configure_chain_url = f"http://34.91.209.79:800/configure_and_load_chain/?session_id={session_id}"
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
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message(message["role"], avatar=st.session_state.user_avatar_url):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar=st.session_state.ai_avatar_url):
                st.markdown(message["content"])

    if prompt := st.chat_input("Scrivi qualcosa"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        #####################################################################
        if len(st.session_state.messages) > 10:
            st.session_state.messages = st.session_state.messages[-10:]
        #####################################################################

        with st.chat_message("user", avatar=st.session_state.user_avatar_url):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=st.session_state.ai_avatar_url):

            uploaded_urls = json.dumps([form for form in st.session_state.url_forms], indent=2)
            input_suffix = f"*NOTE:* - All'occorrenza preleva informazioni utili dai seguenti urls per eseguire al meglio i task richiesti: {uploaded_urls}"
            message_placeholder = st.empty()
            s = requests.Session()
            full_response = ""
            url = f"{api_address}/chains/stream_events_chain"
            payload = {
                "chain_id": f"{session_id}-workflow_generation_chain",
                "query": {
                    "input": prompt + '\n' + input_suffix,
                    "chat_history": st.session_state.messages
                },
                "inference_kwargs": {},
            }

            non_decoded_chunk = b''
            with s.post(url, json=payload, headers=None, stream=True) as resp:
                for chunk in resp.iter_content():
                    if chunk:
                        # Aggiungi il chunk alla sequenza da decodificare
                        non_decoded_chunk += chunk
                        print(chunk)
                        # Decodifica solo quando i byte formano una sequenza UTF-8 completa
                        if is_complete_utf8(non_decoded_chunk):
                            decoded_chunk = non_decoded_chunk.decode("utf-8")
                            full_response += decoded_chunk
                            message_placeholder.markdown(full_response + "▌", unsafe_allow_html=True)
                            non_decoded_chunk = b''  # Svuota il buffer

            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

########################################################################################################################

main()
