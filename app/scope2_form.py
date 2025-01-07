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

# ======================================================
# 2) FUNZIONI PER CARICARE E SALVARE LE LISTE
# ======================================================
def load_list_from_file(filepath):
    """Carica una lista da file JSON, se esiste. Ritorna lista vuota in caso di errore."""
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
    """Salva la lista `data_list` nel file `filepath` in formato JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data_list, f, indent=4, ensure_ascii=False)

# ======================================================
# 3) CARICAMENTO DEI FILE JSON CON I FATTORI DI EMISSIONE (Scope 2)
# ======================================================
def load_json_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# Carichiamo i file dedicati a Scope 2
purchased_electricity_data = load_json_file("purchased_electricity.json")
purchased_heat_or_steam_data = load_json_file("purchased_heat_or_steam.json")
all_data = purchased_electricity_data + purchased_heat_or_steam_data

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
# 5) FUNZIONE PRINCIPALE CHE RENDERIZZA LA PAGINA
# ======================================================
def render_scope2_form():
    """
    Questa funzione costruisce l'interfaccia Streamlit per gestire
    gli asset di Scope 2 (purchased-electricity e purchased-heat-or-steam).
    """

    st.title("Creazione di Asset GHG (Scope 2) - con salvataggio e caricamento da file")

    st.markdown("""
    **Funzionalità**  
    1. Seleziona progressivamente: **ghg_category**, **method**, **type**, **subtype**, **name**, **unit**.  
    2. Aggiungi l'asset a una lista (purchased-electricity o purchased-heat-or-steAM).  
    3. **Visualizza** solo la lista corrispondente alla categoria selezionata.  
    4. **Pulsante** per svuotare la lista della categoria selezionata.  
    5. **Caricamento automatico** dei dati salvati all'avvio (se esistono i file).  
    6. **Pulsante 'Salva Assets'** per salvare su file la lista corrente, sovrascrivendo il contenuto precedente.
    """)

    # Inizializziamo in session_state i contenitori
    if "purchased_electricity_assets_list" not in st.session_state:
        st.session_state["purchased_electricity_assets_list"] = load_list_from_file(
            SAVE_FILES.get("purchased-electricity", "purchased_electricity_assets_list.json")
        )

    if "purchased_heat_or_steam_assets_list" not in st.session_state:
        st.session_state["purchased_heat_or_steam_assets_list"] = load_list_from_file(
            SAVE_FILES.get("purchased-heat-or-steAM", "purchased_heat_or_steam_assets_list.json")
        )

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
            st.warning(f"Trovate {n_rows} righe. Non è possibile dedurre univocamente i campi.")

    # 9) Input per l'asset (nome personalizzato e fattore)
    asset_label = st.text_input("Nome personalizzato per l'asset", "")
    multiplying_factor = st.number_input("Fattore moltiplicativo (es. kWh consumati)", min_value=0.0, value=1.0)

    # Funzione per aggiungere
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

        if selected_category == "purchased-electricity":
            st.session_state["purchased_electricity_assets_list"].append(new_asset)
            st.success(f"Aggiunto a Purchased Electricity: {asset_label}")
        elif selected_category == "purchased-heat-or-steAM":
            st.session_state["purchased_heat_or_steam_assets_list"].append(new_asset)
            st.success(f"Aggiunto a Purchased Heat or Steam: {asset_label}")
        else:
            st.error("Categoria non riconosciuta, impossibile aggiungere l'asset.")

    if st.button("Aggiungi Asset"):
        if n_rows == 1:
            add_asset_to_list()
        else:
            st.error("Impossibile aggiungere. Il filtraggio non è univoco (0 o più di 1 record).")

    # 10) Visualizzazione lista
    st.write("---")
    st.write(f"## Elenco Asset per la Categoria: *{selected_category}*")

    if selected_category == "purchased-electricity":
        category_list = st.session_state["purchased_electricity_assets_list"]
        file_to_save = SAVE_FILES["purchased-electricity"]
    elif selected_category == "purchased-heat-or-steAM":
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
        if st.button("Svuota la lista per la categoria selezionata"):
            if selected_category == "purchased-electricity":
                st.session_state["purchased_electricity_assets_list"] = []
                st.info("Lista 'Purchased Electricity' svuotata.")
            elif selected_category == "purchased-heat-or-steAM":
                st.session_state["purchased_heat_or_steam_assets_list"] = []
                st.info("Lista 'Purchased Heat or Steam' svuotata.")
            else:
                st.warning("Categoria non riconosciuta, impossibile svuotare la lista.")

    with col2:
        if st.button("Salva Assets per la categoria selezionata"):
            if file_to_save:
                # Salva la lista corrente
                if selected_category == "purchased-electricity":
                    save_list_to_file(file_to_save, st.session_state["purchased_electricity_assets_list"])
                elif selected_category == "purchased-heat-or-steAM":
                    save_list_to_file(file_to_save, st.session_state["purchased_heat_or_steam_assets_list"])

                st.success(f"Salvato file '{file_to_save}' con {len(category_list)} asset.")
            else:
                st.error("Categoria non riconosciuta, impossibile salvare.")
