import json
import os

def list_user_sessions(username: str) -> list:
    """
    Restituisce la lista di 'session_id' già esistenti per un dato utente,
    andando a verificare le sottocartelle in USERS_DATA/<username>/.
    """
    base_path = os.path.join("USERS_DATA", username)
    if not os.path.isdir(base_path):
        return []

    # Filtra solo le sottocartelle (ognuna dovrebbe essere un session_id)
    possible_sessions = []
    for item in os.listdir(base_path):
        full_item_path = os.path.join(base_path, item)
        if os.path.isdir(full_item_path):
            # item potrebbe essere un session_id
            possible_sessions.append(item)

    return sorted(possible_sessions)


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

def gather_all_forms_data(username: str, session_id: str) -> str:
    """
    Carica i dati da tutti i file JSON (questionario, scope1, scope2, scope3, ecc.)
    e li concatena in un'unica stringa, che verrà passata all'agente come contesto.
    Inoltre, per il questionario principale, mostra anche le DOMANDE associate
    alle risposte date (se forms.json è disponibile).
    """
    #from ui import get_user_session_forms_dir  # o import della funzione corretta
    # Se la funzione load_questions(...) è in un modulo forms_ui.py:
    from forms_ui import (load_questions)  # Adatta il percorso di import se serve

    forms_dir = get_user_session_forms_dir(username, session_id)
    print(forms_dir)
    if not os.path.exists(forms_dir):
        return ""  # Se non esiste la cartella forms, ritorno stringa vuota

    big_string = ""

    # ---------------------------
    # 1) QUESTIONARIO + DOMANDE
    # ---------------------------
    questionnaire_path = os.path.join(forms_dir, "questionnaire.json")
    if os.path.exists(questionnaire_path):
        # Carichiamo le risposte
        with open(questionnaire_path, "r", encoding="utf-8") as f:
            answers_dict = json.load(f)  # es. { "q_1": "Risposta 1", "q_2": "Risposta 2", ...}

        # Carichiamo la definizione delle domande dal file forms.json
        # (presumendo che tu abbia un load_questions("forms.json") che restituisce una lista)
        try:
            questions_list = load_questions("forms.json")
            # Esempio di struttura:
            # [
            #   { "id": "q_1", "text": "Domanda 1..." },
            #   { "id": "q_2", "text": "Domanda 2..." },
            #   ...
            # ]
        except:
            questions_list = []

        # Ricostruiamo un array di { question: "...", answer: "..." }
        questionnaire_filled = []
        for q_item in questions_list:
            q_id = str(q_item.get("id"))
            q_text = q_item.get("domanda", "")
            user_answer = answers_dict.get(q_id, "")

            questionnaire_filled.append({
                "question": q_text,
                "answer": user_answer,
                "sezione": q_item["sezione"],
                "sotto_sezione": q_item["sotto_sezione"]
            })

        # Aggiungiamo questa struttura al big_string
        big_string += "\n--- QUESTIONARIO COMPILATO (DOMANDA + RISPOSTA) ---\n"
        big_string += json.dumps(questionnaire_filled, ensure_ascii=False, indent=2)

    # ---------------------------
    # 2) SCOPE 1
    # ---------------------------
    scope1_stationary = os.path.join(forms_dir, "stationary_assets_list.json")
    if os.path.exists(scope1_stationary):
        with open(scope1_stationary, "r", encoding="utf-8") as f:
            data_s1_sta = json.load(f)
        big_string += "\n--- SCOPE1: STATIONARY ASSETS ---\n"
        big_string += json.dumps(data_s1_sta, ensure_ascii=False, indent=2)

    scope1_mobile = os.path.join(forms_dir, "mobile_assets_list.json")
    if os.path.exists(scope1_mobile):
        with open(scope1_mobile, "r", encoding="utf-8") as f:
            data_s1_mob = json.load(f)
        big_string += "\n--- SCOPE1: MOBILE ASSETS ---\n"
        big_string += json.dumps(data_s1_mob, ensure_ascii=False, indent=2)

    scope1_fugitive = os.path.join(forms_dir, "fugitive_assets_list.json")
    if os.path.exists(scope1_fugitive):
        with open(scope1_fugitive, "r", encoding="utf-8") as f:
            data_s1_fug = json.load(f)
        big_string += "\n--- SCOPE1: FUGITIVE ASSETS ---\n"
        big_string += json.dumps(data_s1_fug, ensure_ascii=False, indent=2)

    # ---------------------------
    # 3) SCOPE 2
    # ---------------------------
    scope2_elec = os.path.join(forms_dir, "purchased_electricity_assets_list.json")
    if os.path.exists(scope2_elec):
        with open(scope2_elec, "r", encoding="utf-8") as f:
            data_s2_elec = json.load(f)
        big_string += "\n--- SCOPE2: PURCHASED ELECTRICITY ---\n"
        big_string += json.dumps(data_s2_elec, ensure_ascii=False, indent=2)

    scope2_heat = os.path.join(forms_dir, "purchased_heat_or_steam_assets_list.json")
    if os.path.exists(scope2_heat):
        with open(scope2_heat, "r", encoding="utf-8") as f:
            data_s2_heat = json.load(f)
        big_string += "\n--- SCOPE2: PURCHASED HEAT/STEAM ---\n"
        big_string += json.dumps(data_s2_heat, ensure_ascii=False, indent=2)

    # ---------------------------
    # 4) SCOPE 3
    # ---------------------------
    scope3_pgs = os.path.join(forms_dir, "purchased_goods_services_assets_list.json")
    if os.path.exists(scope3_pgs):
        with open(scope3_pgs, "r", encoding="utf-8") as f:
            data_s3_pgs = json.load(f)
        big_string += "\n--- SCOPE3: PURCHASED GOODS & SERVICES ---\n"
        big_string += json.dumps(data_s3_pgs, ensure_ascii=False, indent=2)

    scope3_capital = os.path.join(forms_dir, "capital_goods_assets_list.json")
    if os.path.exists(scope3_capital):
        with open(scope3_capital, "r", encoding="utf-8") as f:
            data_s3_cap = json.load(f)
        big_string += "\n--- SCOPE3: CAPITAL GOODS ---\n"
        big_string += json.dumps(data_s3_cap, ensure_ascii=False, indent=2)

    scope3_upstream_transport = os.path.join(forms_dir, "upstream_transport_assets_list.json")
    if os.path.exists(scope3_upstream_transport):
        with open(scope3_upstream_transport, "r", encoding="utf-8") as f:
            data_s3_upstream = json.load(f)
        big_string += "\n--- SCOPE3: UPSTREAM TRANSPORT ---\n"
        big_string += json.dumps(data_s3_upstream, ensure_ascii=False, indent=2)

    scope3_waste = os.path.join(forms_dir, "waste_generated_assets_list.json")
    if os.path.exists(scope3_waste):
        with open(scope3_waste, "r", encoding="utf-8") as f:
            data_s3_waste = json.load(f)
        big_string += "\n--- SCOPE3: WASTE GENERATED IN OPERATIONS ---\n"
        big_string += json.dumps(data_s3_waste, ensure_ascii=False, indent=2)

    scope3_biz_travel = os.path.join(forms_dir, "business_travel_assets_list.json")
    if os.path.exists(scope3_biz_travel):
        with open(scope3_biz_travel, "r", encoding="utf-8") as f:
            data_s3_biz = json.load(f)
        big_string += "\n--- SCOPE3: BUSINESS TRAVELS ---\n"
        big_string += json.dumps(data_s3_biz, ensure_ascii=False, indent=2)

    scope3_commuting = os.path.join(forms_dir, "employee_commuting_assets_list.json")
    if os.path.exists(scope3_commuting):
        with open(scope3_commuting, "r", encoding="utf-8") as f:
            data_s3_comm = json.load(f)
        big_string += "\n--- SCOPE3: EMPLOYEE COMMUTING ---\n"
        big_string += json.dumps(data_s3_comm, ensure_ascii=False, indent=2)

    scope3_upstream_leased = os.path.join(forms_dir, "upstream_leased_assets_list.json")
    if os.path.exists(scope3_upstream_leased):
        with open(scope3_upstream_leased, "r", encoding="utf-8") as f:
            data_s3_up_leased = json.load(f)
        big_string += "\n--- SCOPE3: UPSTREAM LEASED ASSETS ---\n"
        big_string += json.dumps(data_s3_up_leased, ensure_ascii=False, indent=2)

    scope3_downstream_transport = os.path.join(forms_dir, "downstream_transport_assets_list.json")
    if os.path.exists(scope3_downstream_transport):
        with open(scope3_downstream_transport, "r", encoding="utf-8") as f:
            data_s3_downstream = json.load(f)
        big_string += "\n--- SCOPE3: DOWNSTREAM TRANSPORT & DISTRIBUTION ---\n"
        big_string += json.dumps(data_s3_downstream, ensure_ascii=False, indent=2)

    # Se ci sono altri file, aggiungili con lo stesso schema...

    return big_string


if __name__ == "__main":
    print(gather_all_forms_data("admin", "1b1ca4"))