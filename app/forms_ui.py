import json
import streamlit as st

def load_questions(file_path):
    """Carica le domande da un file JSON."""
    with open(file_path, 'r', encoding="utf-8") as file:
        return json.load(file)

def save_responses(responses, output_path):
    """Salva le risposte date in un file JSON."""
    with open(output_path, 'w', encoding="utf-8") as file:
        json.dump(responses, file, indent=4, ensure_ascii=False)

def render_questionnaire(questions):
    """Renderizza il questionario usando Streamlit."""
    st.title("Questionario ESG")
    responses = {}

    current_section = None
    current_sub_section = None

    for question in questions:
        # Mostra la sezione se cambia
        if question['sezione'] != current_section:
            st.markdown(f"<h2 style='font-size: 24px; margin-top: 20px;'>{question['sezione']}</h2>", unsafe_allow_html=True)
            current_section = question['sezione']
            current_sub_section = None  # Resetta la sottosezione quando cambia la sezione

        # Mostra la sottosezione se cambia
        if question['sotto_sezione'] != current_sub_section:
            st.markdown(f"<h3 style='font-size: 20px; margin-top: 10px;'>{question['sotto_sezione']}</h3>", unsafe_allow_html=True)
            current_sub_section = question['sotto_sezione']

        # Mostra la domanda
        st.markdown(f"<p style='font-size: 16px; margin-top: 10px;'>{question['id']}. {question['domanda']}</p>", unsafe_allow_html=True)

        # Opzioni di risposta
        responses[question['id']] = st.radio(
            label="",
            options=question['risposte'],
            index=0,
            key=f"question_{question['id']}"
        )

    # Pulsante per inviare le risposte
    if st.button("Invia le risposte"):
        save_responses(responses, "responses.json")
        st.success("Risposte salvate con successo!")

    return responses

# Percorso al file JSON contenente le domande
#questions_file = "forms.json"
#questions = load_questions(questions_file)

# Genera la pagina del questionario
#render_questionnaire(questions)
