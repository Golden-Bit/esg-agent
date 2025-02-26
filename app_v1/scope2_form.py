import streamlit as st
import json
import os

# ======================================================
# 1) NOMI FILE DI SALVATAGGIO (Scope 2)
# ======================================================
SAVE_FILES = {
    "purchased-electricity": "purchased_electricity_assets_list.json",
    "purchased-heat-or-steAM": "purchased_heat_or_steam_assets_list.json"
}

def get_user_session_forms_dir(username: str, session_id: str) -> str:
    """
    Ritorna il percorso in cui salvare i JSON dei forms per l'utente e la sessione specificati.
    Esempio: 'USERS_DATA/<username>/<session_id>/forms'.
    """
    base_dir = os.path.join("USERS_DATA", username, session_id)
    forms_dir = os.path.join(base_dir, "forms")
    os.makedirs(forms_dir, exist_ok=True)
    return forms_dir


# ======================================================
# 2) FUNZIONI PER CARICARE E SALVARE LE LISTE
#    - Gestione della directory in base a session_id
# ======================================================
def load_list_from_file(session_id: str, filename: str, username: str = None):
    """
    Carica una lista da file JSON nella directory della sessione.
    Se il file non esiste, restituisce una lista vuota.
    """
    if not username:
        return []  # Se manca username, impossibile accedere alla cartella utente

    forms_dir = get_user_session_forms_dir(username, session_id)
    fullpath = os.path.join(forms_dir, filename)

    if os.path.isfile(fullpath):
        try:
            with open(fullpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []
    return []


def save_list_to_file(session_id: str, filename: str, data_list: list, username: str = None):
    """
    Salva la lista 'data_list' in un file JSON all'interno della directory della sessione.
    """
    if not username:
        return  # Se manca username, non possiamo salvare

    forms_dir = get_user_session_forms_dir(username, session_id)
    fullpath = os.path.join(forms_dir, filename)

    with open(fullpath, "w", encoding="utf-8") as f:
        json.dump(data_list, f, indent=4, ensure_ascii=False)


# ======================================================
# 3) CARICAMENTO DEI FILE JSON CON I FATTORI DI EMISSIONE (Scope 2)
#    Questi file contengono i record con: ghg_category, method, type, ...
# ======================================================
def load_json_file(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

purchased_electricity_data = load_json_file("purchased_electricity.json")
purchased_heat_or_steam_data = load_json_file("purchased_heat_or_steam.json")
all_data = purchased_electricity_data + purchased_heat_or_steam_data

# ======================================================
# 4) FUNZIONI DI UTILITÀ (FILTRI, ECC.)
# ======================================================
def get_unique_values_for_key(data, key):
    """
    Ritorna i valori unici (non-None) per 'key' in 'data',
    in una lista ordinata (escludendo duplicati).
    """
    values = set()
    for d in data:
        val = d.get(key)
        if val is not None:
            values.add(val)
    return sorted(list(values))

def insert_none_option(options_list):
    """
    Inserisce la voce '(nessuna)' come prima opzione.
    """
    return ["(nessuna)"] + options_list

def filter_data(data, filter_dict):
    """
    Filtra la lista 'data' in base ai (key, value) presenti in 'filter_dict'.
    Se value == None, NON filtra su quel campo.
    Altrimenti, matcha solo i record che hanno d.get(key) == value.
    """
    filtered = data
    for k, v in filter_dict.items():
        if v is not None:
            filtered = [d for d in filtered if d.get(k) == v]
    return filtered

# ======================================================
# 5) FUNZIONE PRINCIPALE PER RENDERIZZARE LA PAGINA SCOPE 2
#    Si accetta un parametro session_id per gestire i salvataggi in cartella
# ======================================================
def render_scope2_form(session_id: str):
    """
    Costruisce l'interfaccia Streamlit per gestire gli asset di Scope 2,
    con salvataggio/caricamento basato su session_id in apposite directory.

    Param:
        session_id (str): Identificatore di sessione, usato per determinare
                          la cartella in cui salvare i file JSON.
    """
    st.title("Creazione di Asset GHG (Scope 2)")
    #st.markdown(f"**Session ID** attuale: `{session_id}`")

    st.markdown("""
    **Funzionalità**  
    1. Ogni tendina (categoria, metodo, type, ecc.) contiene l’opzione **"(nessuna)"** (default).  
    2. Se si lascia **"(nessuna)"**, non si filtra su quel campo.  
    3. Possibilità di inserire un **Emission Factor personalizzato** e una **descrizione personalizzata**.  
    4. Aggiungi l'asset a una lista (purchased-electricity o purchased-heat-or-steAM).  
    5. **Visualizza** solo la lista corrispondente.  
    6. **Pulsanti** per svuotare la lista e salvare su file JSON.
    """)

    # 6) Inizializziamo in session_state i contenitori
    # Recuperiamo l'username (se disponibile)
    username = st.session_state.get("username", None)
    if not username:
        st.warning("Attenzione: non sei loggato, quindi non potrai salvare o caricare i form.")
        return

    # Inizializzazione in session_state
    if "purchased_electricity_assets_list" not in st.session_state:
        st.session_state["purchased_electricity_assets_list"] = load_list_from_file(
            session_id, SAVE_FILES["purchased-electricity"], username=username
        )

    if "purchased_heat_or_steam_assets_list" not in st.session_state:
        st.session_state["purchased_heat_or_steam_assets_list"] = load_list_from_file(
            session_id, SAVE_FILES["purchased-heat-or-steAM"], username=username
        )

    # ========== STEP A: ghg_category ===========
    all_categories = get_unique_values_for_key(all_data, "ghg_category")
    all_categories = insert_none_option(all_categories)
    selected_category = st.selectbox("Categoria (ghg_category)", all_categories, index=0)

    if selected_category == "(nessuna)":
        selected_category_value = None
    else:
        selected_category_value = selected_category

    filtered_cat = filter_data(all_data, {"ghg_category": selected_category_value})

    # ========== STEP B: method ===========
    methods_for_cat = get_unique_values_for_key(filtered_cat, "method")
    methods_for_cat = insert_none_option(methods_for_cat)
    selected_method = st.selectbox("Metodo (method)", methods_for_cat, index=0)

    if selected_method == "(nessuna)":
        selected_method_value = None
    else:
        selected_method_value = selected_method

    filtered_method = filter_data(filtered_cat, {"method": selected_method_value})

    # ========== STEP C: type ===========
    types_for_method = get_unique_values_for_key(filtered_method, "type")
    types_for_method = insert_none_option(types_for_method)
    selected_type = st.selectbox("Tipo (type)", types_for_method, index=0)

    if selected_type == "(nessuna)":
        selected_type_value = None
    else:
        selected_type_value = selected_type

    filtered_type = filter_data(filtered_method, {"type": selected_type_value})

    # ========== STEP D: subtype ===========
    subtypes_for_type = get_unique_values_for_key(filtered_type, "subtype")
    subtypes_for_type = insert_none_option(subtypes_for_type)
    selected_subtype = st.selectbox("Sottotipo (subtype)", subtypes_for_type, index=0)

    if selected_subtype == "(nessuna)":
        selected_subtype_value = None
    else:
        selected_subtype_value = selected_subtype

    filtered_subtype = filter_data(filtered_type, {"subtype": selected_subtype_value})

    # ========== STEP E: name ===========
    names_for_subtype = get_unique_values_for_key(filtered_subtype, "name")
    names_for_subtype = insert_none_option(names_for_subtype)
    selected_name = st.selectbox("Nome (name)", names_for_subtype, index=0)

    if selected_name == "(nessuna)":
        selected_name_value = None
    else:
        selected_name_value = selected_name

    filtered_name = filter_data(filtered_subtype, {"name": selected_name_value})

    # ========== STEP F: unit ===========
    units_for_name = get_unique_values_for_key(filtered_name, "unit")
    units_for_name = insert_none_option(units_for_name)
    selected_unit = st.selectbox("Unit (unit)", units_for_name, index=0)

    if selected_unit == "(nessuna)":
        selected_unit_value = None
    else:
        selected_unit_value = selected_unit

    filtered_unit = filter_data(filtered_name, {"unit": selected_unit_value})

    # 8) Mostra emission factor se univoco
    st.markdown("---")
    n_rows = len(filtered_unit)

    if n_rows == 1:
        row = filtered_unit[0]
        deduced_co2_kg = row.get("total_co2_kg", "N/A") or "N/A"
        deduced_source = row.get("source", "Nessun riferimento")
        deduced_description = row.get("description", "Nessuna descrizione")

        st.write(f"**Emission Factor (CO2 Kg)**: {deduced_co2_kg}")
        st.write(f"**Source**: {deduced_source}")
        st.write(f"**Description**: {deduced_description}")
    else:
        deduced_co2_kg = None
        deduced_description = None
        if n_rows == 0:
            st.warning("Nessuna riga corrisponde ai filtri selezionati.")
        else:
            st.warning(f"Sono presenti {n_rows} righe. Non è possibile dedurre univocamente i campi.")

    st.markdown("---")

    # 9) INPUT per personalizzazioni
    asset_label = st.text_input("Nome personalizzato per l'asset", "")
    custom_emission_factor = st.number_input("Custom Emission Factor (kg CO2 eq)", min_value=0.0, value=0.0)
    custom_description = st.text_area("Descrizione personalizzata (opzionale)", "")
    multiplying_factor = st.number_input("Fattore moltiplicativo (es. kWh consumati, etc.)",
                                         min_value=0.0, value=1.0)
    year = st.selectbox("Anno di riferimento",
                        options=[1900 + i for i in range(126)],
                        index=123,  # di default vicino al 2023
                        help="Anno in cui è avvenuta l'attività associata all'emissione")

    # Funzione per aggiungere
    def add_asset_to_list():
        # Se custom_emission_factor > 0, usiamo quello. Altrimenti usiamo deduced_co2_kg
        if custom_emission_factor > 0:
            final_co2_kg = custom_emission_factor
        else:
            final_co2_kg = deduced_co2_kg

        new_asset = {
            "custom_asset_name": asset_label,
            "ghg_category": selected_category_value,
            "method": selected_method_value,
            "type": selected_type_value,
            "subtype": selected_subtype_value,
            "name": selected_name_value,
            "unit": selected_unit_value,
            "description_from_json": deduced_description,
            "custom_description": custom_description,
            "emission_factor_kg": final_co2_kg,
            "multiplying_factor": multiplying_factor,
            "year": year
        }

        if selected_category_value == "purchased-electricity":
            st.session_state["purchased_electricity_assets_list"].append(new_asset)
            st.success(f"Aggiunto asset '{asset_label}' in 'Purchased Electricity'")
        elif selected_category_value == "purchased-heat-or-steAM":
            st.session_state["purchased_heat_or_steam_assets_list"].append(new_asset)
            st.success(f"Aggiunto asset '{asset_label}' in 'Purchased Heat or Steam'")
        else:
            st.error("Categoria non riconosciuta o '(nessuna)', impossibile aggiungere l'asset.")

    if st.button("Aggiungi Asset"):
        # Se c'è 1 riga univoca, ok
        # Oppure EF personalizzato > 0
        if n_rows == 1 or custom_emission_factor > 0:
            add_asset_to_list()
        else:
            st.error("Il filtro non è univoco e non hai inserito un EF personalizzato.")

    # 10) Visualizza la lista associata a selected_category_value
    st.write("---")
    st.write("## Elenco Asset per la Categoria: *{}*".format(selected_category_value or "(nessuna)"))

    if selected_category_value == "purchased-electricity":
        category_list = st.session_state["purchased_electricity_assets_list"]
        file_to_save = SAVE_FILES["purchased-electricity"]
    elif selected_category_value == "purchased-heat-or-steAM":
        category_list = st.session_state["purchased_heat_or_steam_assets_list"]
        file_to_save = SAVE_FILES["purchased-heat-or-steAM"]
    else:
        category_list = []
        file_to_save = None

    with st.expander("Visualizza / Nascondi la lista", expanded=True):
        st.json(category_list)

    # 11) Pulsanti di svuotamento e salvataggio
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Svuota la lista per la categoria selezionata", use_container_width=True):
            if selected_category_value == "purchased-electricity":
                st.session_state["purchased_electricity_assets_list"] = []
                st.info("Lista 'Purchased Electricity' svuotata.")
            elif selected_category_value == "purchased-heat-or-steAM":
                st.session_state["purchased_heat_or_steam_assets_list"] = []
                st.info("Lista 'Purchased Heat or Steam' svuotata.")
            else:
                st.warning("Categoria non riconosciuta o '(nessuna)', impossibile svuotare la lista.")

    with col2:
        if st.button("Salva Assets per la categoria selezionata", use_container_width=True):
            if file_to_save:
                if selected_category_value == "purchased-electricity":
                    save_list_to_file(session_id, file_to_save, st.session_state["purchased_electricity_assets_list"],
                                      username=username)
                elif selected_category_value == "purchased-heat-or-steAM":
                    save_list_to_file(session_id, file_to_save, st.session_state["purchased_heat_or_steam_assets_list"],
                                      username=username)

                st.success(
                    f"Salvato file '{file_to_save}' in 'USERS_DATA/{username}/{session_id}/forms/' con {len(category_list)} asset.")
            else:
                st.error("Categoria non riconosciuta o '(nessuna)', impossibile salvare.")
