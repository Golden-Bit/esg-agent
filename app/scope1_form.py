import streamlit as st
import json
import os

# ======================================================
# 1) NOMI FILE DI SALVATAGGIO (per ciascuna categoria Scope 1)
# ======================================================
SAVE_FILES = {
    "stationary-combustion": "stationary_assets_list.json",
    "mobile-combustion": "mobile_assets_list.json",
    "fugitive-emissions": "fugitive_assets_list.json"
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
#    Con gestione della directory session_id
# ======================================================
def load_list_from_file(session_id, filename, username=None):
    """
    Carica una lista da file JSON in 'USERS_DATA/<username>/<session_id>/forms/<filename>', se esiste.
    Ritorna una lista vuota in caso di errore o file mancante.
    """
    # 1) Ricava la directory forms
    forms_dir = get_user_session_forms_dir(username, session_id)

    # 2) Costruisce il path
    fullpath = os.path.join(forms_dir, filename)

    # 3) Carica il file se esiste
    if os.path.isfile(fullpath):
        try:
            with open(fullpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    return []
        except:
            return []
    else:
        return []


def save_list_to_file(session_id, filename, data_list, username=None):
    """
    Salva la lista 'data_list' in un file JSON all'interno di
    'USERS_DATA/<username>/<session_id>/forms/<filename>',
    creando la directory se non esiste.
    """
    # 1) Ricava la directory forms
    forms_dir = get_user_session_forms_dir(username, session_id)

    # 2) Costruisce il path
    fullpath = os.path.join(forms_dir, filename)

    # 3) Scrive il file
    with open(fullpath, "w", encoding="utf-8") as f:
        json.dump(data_list, f, indent=4, ensure_ascii=False)



# ======================================================
# 3) CARICAMENTO DEI FILE JSON CON I FATTORI DI EMISSIONE (Scope 1)
# ======================================================
def load_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Esempio: i dati "di fattore di emissione" per Scope 1
stationary_combustion_data = load_json_file("stationary_combustion.json")
mobile_combustion_data = load_json_file("mobile_combustion.json")
fugitive_emissions_data = load_json_file("fugitive_emissions.json")

all_data = (
    stationary_combustion_data
    + mobile_combustion_data
    + fugitive_emissions_data
)

# ======================================================
# 4) FUNZIONI DI UTILITÀ (FILTRI, ECC.)
# ======================================================
def get_unique_values_for_key(data, key):
    """
    Ritorna i valori unici (non-None) per 'key' in 'data', in forma di lista ordinata.
    """
    values = set()
    for d in data:
        val = d.get(key)
        if val is not None:
            values.add(val)
    return sorted(list(values))

def insert_none_option(options_list):
    """
    Inserisce l'opzione '(nessuna)' come prima voce.
    Ritorna la lista con '(nessuna)' + le altre voci ordinate.
    """
    return ["(nessuna)"] + options_list  # Se vuoi ordinarle dopo, usa sorted(options_list)

def filter_data(data, filter_dict):
    """
    Filtra la lista 'data' in base ai (key, value) in 'filter_dict'.
    Ritorna solo gli item che matchano TUTTI i campi specificati
    dove value != None.
    """
    filtered = data
    for k, v in filter_dict.items():
        if v is not None:  # filtra solo se v non è None
            filtered = [d for d in filtered if d.get(k) == v]
    return filtered


# ======================================================
# 5) FUNZIONE PRINCIPALE: render_scope1_form(session_id)
#    Richiamata da main.py (o altrove) per mostrare la UI di Scope 1
# ======================================================
def render_scope1_form(session_id: str):
    """
    Costruisce l'interfaccia Streamlit per gestire gli asset di Scope 1
    (Stationary, Mobile e Fugitive) e salva/carica i dati nella cartella 'forms'
    relativa alla sessione.

    Param:
        session_id (str): Identificatore di sessione, usato per
                          salvare i file in "USERS_DATA/<username>/<session_id>/forms".
    """
    st.title("Creazione di Asset GHG (Scope 1)")

    st.markdown("""
    **Funzionalità principali**  
    1. Seleziona progressivamente: **ghg_category**, **method**, **type**, **subtype**, **name**, **unit** (ciascuno con opzione "(nessuna)").  
    2. Aggiungi l'asset a una lista (Stationary, Mobile o Fugitive) in base a `ghg_category`.  
    3. **Possibilità** di inserire un fattore di emissione personalizzato e una descrizione personalizzata.  
    4. **Visualizza** solo la lista corrispondente alla categoria selezionata.  
    5. **Pulsante** per svuotare la lista della categoria selezionata.  
    6. **Caricamento automatico** dei dati salvati all'avvio (se esistono i file).  
    7. **Pulsante 'Salva Asset'** per salvare su file la lista corrente nella directory forms.
    """)

    # Ricaviamo l'username dal session_state (assumendo tu lo salvi lì dopo il login)
    username = st.session_state.get("username", None)
    if not username:
        st.warning("Attenzione: non sei loggato, non potrai salvare/caricare i form in locale.")
        # Puoi decidere se proseguire comunque o fare un return.
        # return

    # ================== 1) CARICAMENTO LISTE DA FILE  ==================
    # Se i file di Scope 1 sono i seguenti (esempio):
    # scope1-stationary.json, scope1-mobile.json, scope1-fugitive.json
    # in una cartella forms/ sotto la sessione:
    # "USERS_DATA/<username>/<session_id>/forms/scope1-stationary.json" etc.
    # supponiamo di avere un dict globale:
    # SAVE_FILES = {
    #   "stationary-combustion": "scope1-stationary.json",
    #   "mobile-combustion": "scope1-mobile.json",
    #   "fugitive-emissions": "scope1-fugitive.json"
    # }

    # L'idea: stiamo inizializzando 3 liste in session_state
    if "stationary_assets_list" not in st.session_state:
        st.session_state["stationary_assets_list"] = load_list_from_file(
            session_id,
            SAVE_FILES["stationary-combustion"],
            username=username  # se la funzione load_list_from_file supporta
        )

    if "mobile_assets_list" not in st.session_state:
        st.session_state["mobile_assets_list"] = load_list_from_file(
            session_id,
            SAVE_FILES["mobile-combustion"],
            username=username
        )

    if "fugitive_assets_list" not in st.session_state:
        st.session_state["fugitive_assets_list"] = load_list_from_file(
            session_id,
            SAVE_FILES["fugitive-emissions"],
            username=username
        )

    # ========== STEP A: CATEGORY ================
    all_categories = get_unique_values_for_key(all_data, "ghg_category")
    all_categories = insert_none_option(all_categories)   # inserisce "(nessuna)"
    selected_category = st.selectbox("Categoria (ghg_category)", all_categories, index=0)

    if selected_category == "(nessuna)":
        selected_category_value = None
    else:
        selected_category_value = selected_category

    filtered_cat = filter_data(all_data, {"ghg_category": selected_category_value})

    # ========== STEP B: METHOD ================
    methods_for_cat = get_unique_values_for_key(filtered_cat, "method")
    methods_for_cat = insert_none_option(methods_for_cat)
    selected_method = st.selectbox("Metodo (method)", methods_for_cat, index=0)

    if selected_method == "(nessuna)":
        selected_method_value = None
    else:
        selected_method_value = selected_method

    filtered_method = filter_data(filtered_cat, {"method": selected_method_value})

    # ========== STEP C: TYPE ================
    types_for_method = get_unique_values_for_key(filtered_method, "type")
    types_for_method = insert_none_option(types_for_method)
    selected_type = st.selectbox("Tipo (type)", types_for_method, index=0)

    if selected_type == "(nessuna)":
        selected_type_value = None
    else:
        selected_type_value = selected_type

    filtered_type = filter_data(filtered_method, {"type": selected_type_value})

    # ========== STEP D: SUBTYPE ================
    subtypes_for_type = get_unique_values_for_key(filtered_type, "subtype")
    subtypes_for_type = insert_none_option(subtypes_for_type)
    selected_subtype = st.selectbox("Sottotipo (subtype)", subtypes_for_type, index=0)

    if selected_subtype == "(nessuna)":
        selected_subtype_value = None
    else:
        selected_subtype_value = selected_subtype

    filtered_subtype = filter_data(filtered_type, {"subtype": selected_subtype_value})

    # ========== STEP E: NAME ================
    names_for_subtype = get_unique_values_for_key(filtered_subtype, "name")
    names_for_subtype = insert_none_option(names_for_subtype)
    selected_name = st.selectbox("Nome (name)", names_for_subtype, index=0)

    if selected_name == "(nessuna)":
        selected_name_value = None
    else:
        selected_name_value = selected_name

    filtered_name = filter_data(filtered_subtype, {"name": selected_name_value})

    # ========== STEP F: UNIT ================
    units_for_name = get_unique_values_for_key(filtered_name, "unit")
    units_for_name = insert_none_option(units_for_name)
    selected_unit = st.selectbox("Unit (unit)", units_for_name, index=0)

    if selected_unit == "(nessuna)":
        selected_unit_value = None
    else:
        selected_unit_value = selected_unit

    filtered_unit = filter_data(filtered_name, {"unit": selected_unit_value})

    # Mostra info emission factor e description se c'è 1 sola riga
    st.markdown("---")

    n_rows = len(filtered_unit)
    if n_rows == 1:
        row = filtered_unit[0]
        deduced_co2_kg = row.get("total_co2_kg", "N/A")
        if not deduced_co2_kg:
            deduced_co2_kg = "N/A"
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
            st.warning(f"Esistono {n_rows} righe corrispondenti. Non è possibile dedurre univocamente i campi.")

    st.markdown("---")

    # ========== STEP G: INPUT UTENTE EXTRA ============
    asset_label = st.text_input("Nome personalizzato per l'asset", "")

    st.write("Puoi inserire facoltativamente un fattore di emissione personalizzato (override del valore dedotto).")
    custom_emission_factor = st.number_input("Custom Emission Factor", min_value=0.0, value=0.0)

    custom_description = st.text_area("Descrizione personalizzata", value="", help="Inserisci una descrizione extra (opzionale).")

    multiplying_factor = st.number_input("Fattore moltiplicativo (opzionale)", min_value=0.0, value=1.0,
                                         help="Ad es. i litri di carburante, i kWh consumati, ecc.")

    year = st.selectbox("Anno di riferimento", options=[1900 + i for i in range(125)], index=123,  # default near 2023
                        help="Anno in cui è avvenuta l'attività associata all'emissione")

    # Funzione helper per aggiungere
    def add_asset_to_list():
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

        # in base a selected_category_value
        if selected_category_value == "stationary-combustion":
            st.session_state["stationary_assets_list"].append(new_asset)
            st.success(f"Aggiunto in Stationary Combustion: {asset_label}")
        elif selected_category_value == "mobile-combustion":
            st.session_state["mobile_assets_list"].append(new_asset)
            st.success(f"Aggiunto in Mobile Combustion: {asset_label}")
        elif selected_category_value == "fugitive-emissions":
            st.session_state["fugitive_assets_list"].append(new_asset)
            st.success(f"Aggiunto in Fugitive Emissions: {asset_label}")
        else:
            st.error("Categoria non riconosciuta, impossibile aggiungere l'asset.")

    if st.button("Aggiungi Asset"):
        # Se n_rows == 1, abbiamo un record univoco, oppure l'utente ha forzato EF custom
        if n_rows == 1 or custom_emission_factor > 0:
            add_asset_to_list()
        else:
            st.error("Impossibile aggiungere. Il filtraggio non è univoco e nessun EF personalizzato è stato inserito.")

    st.write("---")
    st.write("## Elenco Asset per la Categoria: *{}*".format(selected_category_value or "(nessuna)"))

    # Seleziona la lista in base alla categoria
    if selected_category_value == "stationary-combustion":
        category_list = st.session_state["stationary_assets_list"]
        file_to_save = SAVE_FILES["stationary-combustion"]
    elif selected_category_value == "mobile-combustion":
        category_list = st.session_state["mobile_assets_list"]
        file_to_save = SAVE_FILES["mobile-combustion"]
    elif selected_category_value == "fugitive-emissions":
        category_list = st.session_state["fugitive_assets_list"]
        file_to_save = SAVE_FILES["fugitive-emissions"]
    else:
        category_list = []
        file_to_save = None

    with st.expander("Visualizza/Riduci la lista", expanded=True):
        st.json(category_list)

    col1, col2 = st.columns(2)

    # Pulsante per svuotare
    with col1:
        if st.button("Svuota la lista per la categoria selezionata"):
            if selected_category_value == "stationary-combustion":
                st.session_state["stationary_assets_list"] = []
                st.info("Lista Stationary Combustion svuotata.")
            elif selected_category_value == "mobile-combustion":
                st.session_state["mobile_assets_list"] = []
                st.info("Lista Mobile Combustion svuotata.")
            elif selected_category_value == "fugitive-emissions":
                st.session_state["fugitive_assets_list"] = []
                st.info("Lista Fugitive Emissions svuotata.")
            else:
                st.warning("Categoria non riconosciuta o '(nessuna)', impossibile svuotare la lista.")

    # Pulsante per salvare
    with col2:
        if st.button("Salva Assets per la categoria selezionata"):
            if file_to_save:
                # Salviamo la lista attuale su disco
                save_list_to_file(session_id, file_to_save, category_list, username=username)
                st.success(f"Salvato file '{file_to_save}' (forms dir per session '{session_id}') con {len(category_list)} asset.")
            else:
                st.error("Categoria non riconosciuta o '(nessuna)', impossibile salvare.")
