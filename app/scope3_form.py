import streamlit as st
import json
import os

# ======================================================
# 1) NOMI FILE DI SALVATAGGIO (Scope 3)
#    Esempio di categorie: "purchased-goods-and-services", "capital-goods", ecc.
# ======================================================
SAVE_FILES = {
    "purchased-goods-and-services": "purchased_goods_services_assets_list.json",
    "capital-goods": "capital_goods_assets_list.json",
    "upstream-transportation-and-distribution": "upstream_transport_assets_list.json",
    "waste-generated-in-operations": "waste_generated_assets_list.json",
    "business-travels": "business_travel_assets_list.json",
    "employee-commuting": "employee_commuting_assets_list.json",
    "upstream-leased-assets": "upstream_leased_assets_list.json",
    "downstream-transportation-and-distribution": "downstream_transport_assets_list.json"
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
# 2) FUNZIONI PER CARICARE/SALVARE LISTE (session_id)
# ======================================================
def load_list_from_file(session_id: str, filename: str, username: str = None):
    """
    Carica una lista da file JSON all'interno della cartella dell'utente e sessione.
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
# 3) CARICAMENTO DEI FILE JSON CON I FATTORI DI EMISSIONE (Scope 3)
# ======================================================
def load_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

purchased_goods_data = load_json_file("purchased_goods_and_services.json")
capital_goods_data = load_json_file("capital_goods.json")
upstream_transport_data = load_json_file("upstream_transportation_and_distribution.json")
waste_generated_data = load_json_file("waste_generated_in_operations.json")
business_travel_data = load_json_file("business_travels.json")
employee_commuting_data = load_json_file("employee_commuting.json")
upstream_leased_data = load_json_file("upstream_leased_assets.json")
downstream_transport_data = load_json_file("downstream_transportation_and_distribution.json")

all_data = (
    purchased_goods_data
    + capital_goods_data
    + upstream_transport_data
    + waste_generated_data
    + business_travel_data
    + employee_commuting_data
    + upstream_leased_data
    + downstream_transport_data
)

# ======================================================
# 4) FUNZIONI DI UTILITÀ (filtri, estrazione valori unici, ecc.)
# ======================================================
def get_unique_values_for_key(data, key):
    """
    - Leggiamo i valori da 'key'
    - Convertiamo tutto in stringa (str(val)) per evitare errori di ordinamento
      se ci sono mix di float/str
    - Restituiamo la lista ordinata
    """
    values = set()
    for d in data:
        val = d.get(key)
        if val is not None:
            # Forziamo la conversione in stringa
            values.add(str(val))
    return sorted(values)

def insert_none_option(options_list):
    """
    Inserisce la stringa '(nessuna)' come prima voce,
    così che la selectbox abbia un'opzione per non filtrare su quel campo.
    """
    return ["(nessuna)"] + options_list

def filter_data(data, filter_dict):
    """
    Filtra la lista 'data' in base ai (key, value) specificati in 'filter_dict'.
    Ritorna solo gli item che matchano TUTTI i campi (se value != None).
    """
    filtered = data
    for k, v in filter_dict.items():
        if v is not None:
            # NOTA: poiché in get_unique_values_for_key abbiamo convertito in stringa,
            # se i record originali in data sono float, potremmo dover convertire i record in string.
            # In un contesto reale, devi gestire la coerenza dei tipi.
            filtered = [d for d in filtered if str(d.get(k)) == v]
    return filtered

# ======================================================
# 5) FUNZIONE PRINCIPALE CHE RENDERIZZA LA PAGINA SCOPE 3
# ======================================================
def render_scope3_form(session_id: str):
    """
    Costruisce l'interfaccia Streamlit per gestire gli asset di Scope 3,
    consentendo di salvare/caricare i dati in base alla directory `session_id`.
    """

    st.title("Creazione di Asset GHG (Scope 3)")
    #st.markdown(f"**Session ID**: `{session_id}`")

    st.markdown("""
    **Funzionalità**  
    1. Ogni selectbox parte con **'(nessuna)'** così da poter NON filtrare se non si desidera.  
    2. Evitiamo l'errore di sorting misto tra string e float forzando la conversione a string.  
    3. Se c'è un solo record univoco **o** se l'utente definisce un EF personalizzato, possiamo aggiungere l'asset.
    """)


    # Recuperiamo l'username (se disponibile)
    username = st.session_state.get("username", None)
    if not username:
        st.warning("Attenzione: non sei loggato, quindi non potrai salvare o caricare i form.")
        return

    # Inizializziamo le liste in session_state
    for cat_key, filename in SAVE_FILES.items():
        ss_key = f"{cat_key}_assets_list"
        if ss_key not in st.session_state:
            st.session_state[ss_key] = load_list_from_file(session_id, filename, username=username)

    # STEP 1: ghg_category
    all_categories = get_unique_values_for_key(all_data, "ghg_category")
    all_categories = insert_none_option(all_categories)
    selected_category = st.selectbox("Categoria (ghg_category)", all_categories, index=0)

    if selected_category == "(nessuna)":
        selected_category_value = None
    else:
        selected_category_value = selected_category

    filtered_cat = filter_data(all_data, {"ghg_category": selected_category_value})

    # STEP 2: method
    methods_for_cat = get_unique_values_for_key(filtered_cat, "method")
    methods_for_cat = insert_none_option(methods_for_cat)
    selected_method = st.selectbox("Metodo (method)", methods_for_cat, index=0)

    if selected_method == "(nessuna)":
        selected_method_value = None
    else:
        selected_method_value = selected_method

    filtered_method = filter_data(filtered_cat, {"method": selected_method_value})

    # STEP 3: type
    types_for_method = get_unique_values_for_key(filtered_method, "type")
    types_for_method = insert_none_option(types_for_method)
    selected_type = st.selectbox("Tipo (type)", types_for_method, index=0)

    if selected_type == "(nessuna)":
        selected_type_value = None
    else:
        selected_type_value = selected_type

    filtered_type = filter_data(filtered_method, {"type": selected_type_value})

    # STEP 4: subtype
    subtypes_for_type = get_unique_values_for_key(filtered_type, "subtype")
    subtypes_for_type = insert_none_option(subtypes_for_type)
    selected_subtype = st.selectbox("Sottotipo (subtype)", subtypes_for_type, index=0)

    if selected_subtype == "(nessuna)":
        selected_subtype_value = None
    else:
        selected_subtype_value = selected_subtype

    filtered_subtype = filter_data(filtered_type, {"subtype": selected_subtype_value})

    # STEP 5: name
    names_for_subtype = get_unique_values_for_key(filtered_subtype, "name")
    names_for_subtype = insert_none_option(names_for_subtype)
    selected_name = st.selectbox("Nome (name)", names_for_subtype, index=0)

    if selected_name == "(nessuna)":
        selected_name_value = None
    else:
        selected_name_value = selected_name

    filtered_name = filter_data(filtered_subtype, {"name": selected_name_value})

    # STEP 6: unit
    units_for_name = get_unique_values_for_key(filtered_name, "unit")
    units_for_name = insert_none_option(units_for_name)
    selected_unit = st.selectbox("Unit (unit)", units_for_name, index=0)

    if selected_unit == "(nessuna)":
        selected_unit_value = None
    else:
        selected_unit_value = selected_unit

    filtered_unit = filter_data(filtered_name, {"unit": selected_unit_value})

    st.markdown("---")

    # Verifichiamo se c'è un singolo record
    n_rows = len(filtered_unit)
    if n_rows == 1:
        row = filtered_unit[0]
        # Forzando a str() nelle comparazioni e sorting, i record originali restano invariati
        deduced_co2_kg = str(row.get("total_co2_kg", "N/A"))
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
            st.warning(f"Trovate {n_rows} righe. Non è possibile dedurre un EF univoco.")

    st.markdown("---")

    # Campi personalizzati
    asset_label = st.text_input("Nome personalizzato per l'asset", "")
    custom_emission_factor = st.number_input("Custom Emission Factor (kg CO2e)", min_value=0.0, value=0.0)
    custom_description = st.text_area("Descrizione personalizzata (opzionale)", "")
    multiplying_factor = st.number_input("Fattore moltiplicativo (opzionale)", min_value=0.0, value=1.0)
    year = st.selectbox("Anno di riferimento", options=[1900 + i for i in range(125)], index=123)

    # Funzione di aggiunta
    def add_asset_to_list():
        if custom_emission_factor > 0:
            final_co2_kg = str(custom_emission_factor)
        else:
            final_co2_kg = deduced_co2_kg  # è già str (o None)

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

        ss_key = f"{selected_category_value}_assets_list" if selected_category_value else None
        if ss_key and ss_key in st.session_state:
            st.session_state[ss_key].append(new_asset)
            st.success(f"Aggiunto asset '{asset_label}' in '{selected_category_value}'.")
        else:
            st.error(f"Categoria {selected_category_value} non riconosciuta o '(nessuna)'; impossibile aggiungere l'asset.")

    if st.button("Aggiungi Asset"):
        if n_rows == 1 or custom_emission_factor > 0:
            add_asset_to_list()
        else:
            st.error("Il filtraggio non è univoco e nessun EF personalizzato è stato inserito.")

    st.write("---")
    st.write(f"## Elenco Asset per la Categoria: *{selected_category_value or '(nessuna)'}*")

    ss_key_for_list = f"{selected_category_value}_assets_list" if selected_category_value else None
    if ss_key_for_list and ss_key_for_list in st.session_state:
        category_list = st.session_state[ss_key_for_list]
        file_to_save = SAVE_FILES.get(selected_category_value, None)
    else:
        category_list = []
        file_to_save = None

    with st.expander("Visualizza / Nascondi la lista", expanded=True):
        st.json(category_list)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Svuota la lista per la categoria selezionata"):
            if file_to_save and ss_key_for_list in st.session_state:
                st.session_state[ss_key_for_list] = []
                st.info(f"Lista '{selected_category_value}' svuotata.")
            else:
                st.warning("Categoria non riconosciuta o '(nessuna)', impossibile svuotare la lista.")

    with col2:
        if st.button("Salva Assets per la categoria selezionata"):
            if file_to_save:
                save_list_to_file(session_id, file_to_save, category_list, username=username)
                st.success(
                    f"Salvato file '{file_to_save}' in 'USERS_DATA/{username}/{session_id}/forms/' con {len(category_list)} asset.")
            else:
                st.error("Categoria non riconosciuta o '(nessuna)', impossibile salvare.")

