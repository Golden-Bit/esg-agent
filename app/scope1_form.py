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

# ======================================================
# 2) FUNZIONI PER CARICARE E SALVARE LE LISTE
# ======================================================
def load_list_from_file(filepath):
    """
    Tenta di caricare da 'filepath' e restituire la lista.
    Se il file non esiste o è corrotto, ritorna una lista vuota.
    """
    if os.path.isfile(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    return []
        except:
            return []
    else:
        return []

def save_list_to_file(filepath, data_list):
    """
    Salva la lista 'data_list' nel file 'filepath', sovrascrivendo il contenuto.
    """
    with open(filepath, "w", encoding="utf-8") as f:
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

def filter_data(data, filter_dict):
    """
    Filtra la lista 'data' in base ai (key, value) in 'filter_dict'.
    Ritorna solo gli item che matchano TUTTI i campi specificati.
    """
    filtered = data
    for k, v in filter_dict.items():
        if v is not None:
            filtered = [d for d in filtered if d.get(k) == v]
    return filtered

# ======================================================
# 5) FUNZIONE PRINCIPALE: render_scope1_form()
#    Richiamata da main.py per mostrare la pagina Streamlit di Scope 1
# ======================================================
def render_scope1_form():
    """
    Costruisce l'interfaccia Streamlit per gestire gli asset di Scope 1
    (Stationary, Mobile e Fugitive).
    """
    st.title("Creazione di Asset GHG (Scope 1) - con salvataggio e caricamento da file")

    st.markdown("""
    **Funzionalità principali**  
    1. Seleziona progressivamente: **ghg_category**, **method**, **type**, **subtype**, **name**, **unit**.  
    2. Aggiungi l'asset a una lista (Stationary, Mobile o Fugitive) in base a `ghg_category`.  
    3. **Visualizza** solo la lista corrispondente alla categoria selezionata.  
    4. **Pulsante** per svuotare la lista della categoria selezionata.  
    5. **Caricamento automatico** dei dati salvati all'avvio (se esistono i file).  
    6. **Pulsante 'Salva Asset'** per salvare su file la lista corrente, sovrascrivendo il contenuto precedente.
    """)

    # (6) Inizializzazione delle liste in session_state (caricamento dai file se esistono)
    if "stationary_assets_list" not in st.session_state:
        st.session_state["stationary_assets_list"] = load_list_from_file(SAVE_FILES["stationary-combustion"])

    if "mobile_assets_list" not in st.session_state:
        st.session_state["mobile_assets_list"] = load_list_from_file(SAVE_FILES["mobile-combustion"])

    if "fugitive_assets_list" not in st.session_state:
        st.session_state["fugitive_assets_list"] = load_list_from_file(SAVE_FILES["fugitive-emissions"])

    # 7) Selezione progressiva
    all_categories = get_unique_values_for_key(all_data, "ghg_category")
    selected_category = st.selectbox("Categoria (ghg_category)", all_categories)

    filtered_cat = filter_data(all_data, {"ghg_category": selected_category})

    methods_for_cat = get_unique_values_for_key(filtered_cat, "method")
    selected_method = st.selectbox("Metodo (method)", methods_for_cat)

    filtered_method = filter_data(filtered_cat, {"method": selected_method})

    types_for_method = get_unique_values_for_key(filtered_method, "type")
    selected_type = st.selectbox("Tipo (type)", types_for_method)

    filtered_type = filter_data(filtered_method, {"type": selected_type})

    subtypes_for_type = get_unique_values_for_key(filtered_type, "subtype")
    if not subtypes_for_type:
        subtypes_for_type = ["(nessuna)"]
    selected_subtype = st.selectbox("Sottotipo (subtype)", subtypes_for_type)

    if selected_subtype == "(nessuna)":
        selected_subtype = None

    filtered_subtype = filter_data(filtered_type, {"subtype": selected_subtype})

    names_for_subtype = get_unique_values_for_key(filtered_subtype, "name")
    if not names_for_subtype:
        names_for_subtype = ["(nessuno)"]
    selected_name = st.selectbox("Nome (name)", names_for_subtype)

    if selected_name == "(nessuno)":
        selected_name = None

    filtered_name = filter_data(filtered_subtype, {"name": selected_name})

    units_for_name = get_unique_values_for_key(filtered_name, "unit")
    if not units_for_name:
        units_for_name = ["(nessuna)"]
    selected_unit = st.selectbox("Unit (unit)", units_for_name)

    if selected_unit == "(nessuna)":
        selected_unit = None

    filtered_unit = filter_data(filtered_name, {"unit": selected_unit})

    # 8) Mostra emission factor se univoco
    n_rows = len(filtered_unit)
    if n_rows == 1:
        row = filtered_unit[0]
        deduced_co2_kg = row.get("total_co2_kg", "N/A")
        deduced_description = row.get("description", "Nessuna descrizione")
        st.write(f"**Emission Factor** (`total_co2_kg`): {deduced_co2_kg}")
        st.write(f"**Description**: {deduced_description}")
    else:
        deduced_co2_kg = None
        deduced_description = None
        if n_rows == 0:
            st.warning("Nessuna riga corrisponde ai filtri selezionati.")
        else:
            st.warning(f"Esistono {n_rows} righe corrispondenti. Non è possibile dedurre univocamente i campi.")

    # 9) Input per l'asset
    asset_label = st.text_input("Nome personalizzato per l'asset", "")
    multiplying_factor = st.number_input("Fattore moltiplicativo (opzionale)", min_value=0.0, value=1.0)

    # 10) Funzione per aggiungere
    def add_asset_to_list():
        new_asset = {
            "custom_asset_name": asset_label,
            "ghg_category": selected_category,
            "method": selected_method,
            "type": selected_type,
            "subtype": selected_subtype,
            "name": selected_name,
            "unit": selected_unit,
            "description": deduced_description,
            "emission_factor_kg": deduced_co2_kg,
            "multiplying_factor": multiplying_factor
        }

        if selected_category == "stationary-combustion":
            st.session_state["stationary_assets_list"].append(new_asset)
            st.success(f"Aggiunto in Stationary Combustion: {asset_label}")
        elif selected_category == "mobile-combustion":
            st.session_state["mobile_assets_list"].append(new_asset)
            st.success(f"Aggiunto in Mobile Combustion: {asset_label}")
        elif selected_category == "fugitive-emissions":
            st.session_state["fugitive_assets_list"].append(new_asset)
            st.success(f"Aggiunto in Fugitive Emissions: {asset_label}")
        else:
            st.error("Categoria non riconosciuta, impossibile aggiungere l'asset.")

    if st.button("Aggiungi Asset"):
        if n_rows == 1:
            add_asset_to_list()
        else:
            st.error("Impossibile aggiungere. Il filtraggio non è univoco (0 o più di 1 record).")

    # 11) Visualizza la lista
    st.write("---")
    st.write(f"## Elenco Asset per la Categoria: *{selected_category}*")

    if selected_category == "stationary-combustion":
        category_list = st.session_state["stationary_assets_list"]
        file_to_save = SAVE_FILES["stationary-combustion"]
    elif selected_category == "mobile-combustion":
        category_list = st.session_state["mobile_assets_list"]
        file_to_save = SAVE_FILES["mobile-combustion"]
    elif selected_category == "fugitive-emissions":
        category_list = st.session_state["fugitive_assets_list"]
        file_to_save = SAVE_FILES["fugitive-emissions"]
    else:
        category_list = []
        file_to_save = None

    with st.expander("Visualizza/Riduci la lista", expanded=True):
        st.json(category_list)

    # 12) Pulsanti per svuotare o salvare
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Svuota la lista per la categoria selezionata"):
            if selected_category == "stationary-combustion":
                st.session_state["stationary_assets_list"] = []
                st.info("Lista Stationary Combustion svuotata.")
            elif selected_category == "mobile-combustion":
                st.session_state["mobile_assets_list"] = []
                st.info("Lista Mobile Combustion svuotata.")
            elif selected_category == "fugitive-emissions":
                st.session_state["fugitive_assets_list"] = []
                st.info("Lista Fugitive Emissions svuotata.")
            else:
                st.warning("Categoria non riconosciuta, impossibile svuotare la lista.")

    with col2:
        if st.button("Salva Assets per la categoria selezionata"):
            if file_to_save:
                # Salva la lista corrente
                if selected_category == "stationary-combustion":
                    save_list_to_file(file_to_save, st.session_state["stationary_assets_list"])
                elif selected_category == "mobile-combustion":
                    save_list_to_file(file_to_save, st.session_state["mobile_assets_list"])
                elif selected_category == "fugitive-emissions":
                    save_list_to_file(file_to_save, st.session_state["fugitive_assets_list"])

                st.success(f"Salvato file '{file_to_save}' con {len(category_list)} asset.")
            else:
                st.error("Categoria non riconosciuta, impossibile salvare.")
