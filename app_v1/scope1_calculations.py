import json
import os
from collections import defaultdict

#############################
# 1) DEFINIZIONE DEI VALORI DI RIFERIMENTO
#############################

# Valori di riferimento standard
DEFAULT_FUEL_CONSUMED = 1000.0  # litri o kg
DEFAULT_EMISSION_FACTOR_KG = 2.5  # kg CO2e per litro o kg di combustibile
DEFAULT_BEGIN_YEAR_STORAGE = 5000.0  # kg
DEFAULT_END_YEAR_STORAGE = 4500.0  # kg
DEFAULT_PURCHASED = 1000.0  # kg
DEFAULT_ACQUIRED = 500.0  # kg
DEFAULT_GAS_GWP = 25.0  # Global Warming Potential
DEFAULT_QUANTITY = 100.0  # unità
DEFAULT_CAPACITY = 10.0  # unità
DEFAULT_EMISSION_FACTOR_FUGITIVE_KG = 1.2  # kg CO2e per unità
DEFAULT_METHOD = "mass_balance_method"  # metodo predefinito per fugitive emissions

#############################
# 2) FUNZIONI DI CALCOLO SCOPE 1
#############################

def calculate_stationary_combustion_emissions(fuel_consumed, emission_factor):
    """
    Stationary Combustion: Emissioni in kg = fuel_consumed (litri o kg) * emission_factor (kgCO2/litro o kg).
    """
    total_kg = fuel_consumed * emission_factor
    total_tonnes = total_kg / 1000
    return total_kg, total_tonnes


def calculate_mobile_combustion_emissions(fuel_consumed, emission_factor):
    """
    Mobile Combustion: Emissioni in kg = fuel_consumed (litri o kg) * emission_factor (kgCO2/litro o kg).
    """
    total_kg = fuel_consumed * emission_factor
    total_tonnes = total_kg / 1000
    return total_kg, total_tonnes


def calculate_fugitive_mass_balance(begin_year_storage, end_year_storage, purchased, acquired):
    """
    Fugitive Emissions (Mass Balance): Emissioni = (begin_year_storage - end_year_storage) + (purchased + acquired).
    """
    decrease = begin_year_storage - end_year_storage
    total_kg = decrease + purchased + acquired
    total_tonnes = total_kg / 1000
    return total_kg, total_tonnes


def calculate_fugitive_screening(quantity, capacity, gas_gwp, emission_factor):
    """
    Fugitive Emissions (Screening): Emissioni = EF * GWP * (quantity * capacity).
    Ritorna (kg, tonnes).
    """
    total_kg = emission_factor * gas_gwp * quantity * capacity
    total_tonnes = total_kg / 1000
    return total_kg, total_tonnes

#############################
# 3) FUNZIONE PRINCIPALE PER CALCOLARE LE EMISSIONI SCOPE 1
#############################

def compute_scope1_emissions(session_id: str):
    """
    Legge i file JSON (stationary_assets_list.json, mobile_assets_list.json, fugitive_assets_list.json),
    applica le formule di calcolo, e restituisce un dizionario con le emissioni raggruppate per anno,
    includendo le fonti.
    """
    # Directory di salvataggio
    session_dir = os.path.join(".", session_id)

    # File di salvataggio per Scope 1
    SAVE_FILES = {
        "stationary_combustion": "stationary_assets_list.json",
        "mobile_combustion": "mobile_assets_list.json",
        "fugitive_emissions": "fugitive_assets_list.json"
    }

    # Funzione di caricamento
    def load_list_from_file(session_id: str, filename: str):
        fullpath = os.path.join(session_dir, filename)
        if os.path.isfile(fullpath):
            with open(fullpath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                except json.JSONDecodeError:
                    print(f"Errore nel decodificare il file JSON: {filename}")
        else:
            print(f"File non trovato: {filename}")
        return []

    # Carica le liste di asset per ciascuna categoria
    scope1_assets = {}
    for category, filename in SAVE_FILES.items():
        scope1_assets[category] = load_list_from_file(session_id, filename)

    # Dati finali raggruppati per anno
    results = defaultdict(lambda: {
        "stationary_combustion_kg": 0.0,
        "mobile_combustion_kg": 0.0,
        "fugitive_emissions_kg": 0.0,
        "total_kg": 0.0,
        "sources": []  # Aggiunto per tracciare le fonti
    })

    # Mappa categorie a funzioni di calcolo
    calculation_functions = {
        "stationary_combustion": calculate_stationary_combustion_emissions,
        "mobile_combustion": calculate_mobile_combustion_emissions,
        "fugitive_emissions": {
            "mass_balance_method": calculate_fugitive_mass_balance,
            "screening_method": calculate_fugitive_screening
        }
    }

    # Itera su ogni categoria e calcola le emissioni
    for category, assets in scope1_assets.items():
        for asset in assets:
            year = asset.get("year", 2023)  # Default se mancante

            if category in ["stationary_combustion", "mobile_combustion"]:
                # Per Stationary e Mobile Combustion
                fuel_consumed = asset.get("multiplying_factor", DEFAULT_FUEL_CONSUMED)
                emission_factor_kg = float(asset.get("emission_factor_kg", DEFAULT_EMISSION_FACTOR_KG))
                calc_func = calculation_functions.get(category, None)
                if calc_func:
                    emission_kg, emission_tonnes = calc_func(fuel_consumed, emission_factor_kg)

                    # Aggiorna i risultati per anno
                    key = f"{category}_kg"
                    results[year][key] += emission_kg
                    results[year]["total_kg"] += emission_kg

                    # Aggiungi le informazioni sulla fonte
                    source_info = {
                        "asset_name": asset.get("custom_asset_name", "Unknown"),
                        "category": category,
                        "method": "spend_based" if category == "stationary_combustion" else "mobile_combustion",
                        "multiplying_factor": fuel_consumed,
                        "emissions_kg": emission_kg,
                        "emissions_tonnes": emission_tonnes,
                        "source": asset.get("source", "Unknown"),
                        "source_year": asset.get("source_year", "Unknown")
                    }
                    results[year]["sources"].append(source_info)
                else:
                    print(f"Categoria '{category}' non riconosciuta.")

            elif category == "fugitive_emissions":
                # Per Fugitive Emissions
                method = asset.get("method", DEFAULT_METHOD).lower()
                calc_func = calculation_functions["fugitive_emissions"].get(method, None)
                if calc_func:
                    if method == "mass_balance_method":
                        begin_year_storage = asset.get("multiplying_factor", DEFAULT_BEGIN_YEAR_STORAGE)
                        end_year_storage = 0 #asset.get("end_year_storage", DEFAULT_END_YEAR_STORAGE)
                        purchased = asset.get("purchased", DEFAULT_PURCHASED)
                        acquired = asset.get("acquired", DEFAULT_ACQUIRED)
                        emission_kg, emission_tonnes = calc_func(
                            begin_year_storage, end_year_storage, purchased, acquired
                        )
                    elif method == "screening_method":
                        quantity = asset.get("multiplying_factor", DEFAULT_QUANTITY)
                        capacity = asset.get("capacity", DEFAULT_CAPACITY)
                        gas_gwp = float(asset.get("gas_gwp", DEFAULT_GAS_GWP))
                        emission_factor = float(asset.get("emission_factor_kg", DEFAULT_EMISSION_FACTOR_FUGITIVE_KG))
                        emission_kg, emission_tonnes = calc_func(
                            quantity, capacity, gas_gwp, emission_factor
                        )
                    else:
                        emission_kg, emission_tonnes = 0.0, 0.0  # Metodo non riconosciuto

                    # Aggiorna i risultati per anno
                    key = "fugitive_emissions_kg"
                    results[year][key] += emission_kg
                    results[year]["total_kg"] += emission_kg

                    # Aggiungi le informazioni sulla fonte
                    source_info = {
                        "asset_name": asset.get("custom_asset_name", "Unknown"),
                        "category": category,
                        "method": method,
                        "multiplying_factor": asset.get("multiplying_factor", 1.0),  # Può variare in base al metodo
                        "emissions_kg": emission_kg,
                        "emissions_tonnes": emission_tonnes,
                        "source": asset.get("source", "Unknown"),
                        "source_year": asset.get("source_year", "Unknown")
                    }
                    results[year]["sources"].append(source_info)
                else:
                    print(f"Metodo '{method}' non riconosciuto per la categoria '{category}'.")

    # Converti i risultati in un dizionario normale
    final_output = {}
    for year, data in results.items():
        final_output[year] = data.copy()
        # Aggiungi le tonnellate (già calcolate nelle funzioni di calcolo)
    return final_output

#############################
# 4) ESEMPIO DI UTILIZZO
#############################

if __name__ == "__main__":
    # Esempio di session_id
    session_id = "my_session_scope1"

    emissions = compute_scope1_emissions(session_id)

    # Stampa un report semplice
    print("Risultati calcolo Scope 1 (raggruppati per anno):")
    for year in sorted(emissions.keys()):
        data = emissions[year]
        print(f"\nAnno: {year}")
        print(
            f"  Stationary Combustion (kg): {data.get('stationary_combustion_kg', 0.0):.2f} | (ton): {data.get('stationary_combustion_kg', 0.0) / 1000:.2f}")
        print(
            f"  Mobile Combustion (kg):    {data.get('mobile_combustion_kg', 0.0):.2f} | (ton): {data.get('mobile_combustion_kg', 0.0) / 1000:.2f}")
        print(
            f"  Fugitive Emissions (kg):   {data.get('fugitive_emissions_kg', 0.0):.2f} | (ton): {data.get('fugitive_emissions_kg', 0.0) / 1000:.2f}")
        print(
            f"  Total Emissions (kg):      {data.get('total_kg', 0.0):.2f} | (ton): {data.get('total_kg', 0.0) / 1000:.2f}")

        # Stampa le fonti
        if data.get("sources"):
            print("  Fonti delle Emissioni:")
            for source in data["sources"]:
                print(
                    f"    - Asset: {source['asset_name']}, Categoria: {source['category']}, Metodo: {source['method']}, Quantità: {source['multiplying_factor']}, Emissioni: {source['emissions_kg']:.2f} kg ({source['emissions_tonnes']:.2f} ton), Fonte: {source['source']}, Anno Fonte: {source['source_year']}")
