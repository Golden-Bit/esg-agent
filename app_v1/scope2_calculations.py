import json
import os
from collections import defaultdict

#############################
# 1) DEFINIZIONE DEI VALORI DI RIFERIMENTO
#############################

# Valori di riferimento standard
DEFAULT_ELECTRICITY_CONSUMED_KWH = 10000.0  # kWh
DEFAULT_HEAT_OR_STEAM_CONSUMED_KWH = 5000.0  # kWh
DEFAULT_EMISSION_FACTOR_ELECTRICITY_KG = 0.5  # kg CO2/kWh
DEFAULT_EMISSION_FACTOR_HEAT_STEAM_KG = 0.3  # kg CO2/kWh
DEFAULT_METHOD_LOCATION_BASED = "location_based"
DEFAULT_METHOD_MARKET_BASED = "market_based"
DEFAULT_METHOD = DEFAULT_METHOD_LOCATION_BASED  # Metodo predefinito

#############################
# 2) FUNZIONI DI CALCOLO SCOPE 2
#############################

def calculate_purchased_electricity_emissions(electricity_consumed, emission_factor, method="location_based"):
    """
    Calcola le emissioni per l'elettricità acquistata.

    Args:
        electricity_consumed (float): Elettricità consumata in kWh.
        emission_factor (float): Fattore di emissione in kgCO2/kWh.
        method (str): Metodo di calcolo ('location_based' o 'market_based').

    Returns:
        tuple: Emissioni totali in kg e tonnellate.
    """
    total_kg = electricity_consumed * emission_factor
    total_tonnes = total_kg / 1000
    return total_kg, total_tonnes


def calculate_purchased_heat_steam_emissions(heat_or_steam_consumed, emission_factor, method="location_based"):
    """
    Calcola le emissioni per il calore o il vapore acquistato.

    Args:
        heat_or_steam_consumed (float): Calore o vapore consumato in kWh.
        emission_factor (float): Fattore di emissione in kgCO2/kWh.
        method (str): Metodo di calcolo ('location_based' o 'market_based').

    Returns:
        tuple: Emissioni totali in kg e tonnellate.
    """
    total_kg = heat_or_steam_consumed * emission_factor
    total_tonnes = total_kg / 1000
    return total_kg, total_tonnes

#############################
# 3) FUNZIONE PRINCIPALE PER CALCOLARE LE EMISSIONI SCOPE 2
#############################

def compute_scope2_emissions(session_id: str):
    """
    Legge i file JSON di Scope 2, applica le formule di calcolo,
    e restituisce un dizionario con le emissioni raggruppate per anno,
    includendo le fonti.

    Args:
        session_id (str): Identificatore di sessione, usato per determinare
                          la cartella in cui salvare i file JSON.

    Returns:
        dict: Emissioni raggruppate per anno.
    """
    # Directory di salvataggio
    session_dir = os.path.join(".", session_id)

    # File di salvataggio per Scope 2
    SAVE_FILES = {
        "purchased_electricity": "purchased_electricity_assets_list.json",
        "purchased_heat_or_steam": "purchased_heat_or_steam_assets_list.json"
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
    scope2_assets = {}
    for category, filename in SAVE_FILES.items():
        scope2_assets[category] = load_list_from_file(session_id, filename)

    # Dati finali raggruppati per anno
    results = defaultdict(lambda: {
        "purchased_electricity_kg": 0.0,
        "purchased_heat_or_steam_kg": 0.0,
        "total_kg": 0.0,
        "sources": []  # Aggiunto per tracciare le fonti
    })

    # Mappa categorie a funzioni di calcolo
    calculation_functions = {
        "purchased_electricity": calculate_purchased_electricity_emissions,
        "purchased_heat_or_steam": calculate_purchased_heat_steam_emissions
    }

    # Itera su ogni categoria e calcola le emissioni
    for category, assets in scope2_assets.items():
        for asset in assets:
            year = asset.get("year", 2023)  # Default se mancante
            emission_factor = float(asset.get("emission_factor_kg", 0.0))  # kgCO2/kWh
            consumed = float(asset.get("multiplying_factor", 0.0))  # kWh
            method = asset.get("method", DEFAULT_METHOD).lower()

            calc_func = calculation_functions.get(category, None)
            if calc_func:
                if category == "purchased_electricity":
                    total_kg, total_tonnes = calc_func(consumed, emission_factor, method)
                    key_kg = "purchased_electricity_kg"
                elif category == "purchased_heat_or_steam":
                    total_kg, total_tonnes = calc_func(consumed, emission_factor, method)
                    key_kg = "purchased_heat_or_steam_kg"
                else:
                    total_kg, total_tonnes = 0.0, 0.0
                    key_kg = "unknown_category_kg"

                # Aggiorna i risultati per anno
                results[year][key_kg] += total_kg
                results[year]["total_kg"] += total_kg

                # Aggiungi le informazioni sulla fonte
                source_info = {
                    "asset_name": asset.get("custom_asset_name", "Unknown"),
                    "category": category,
                    "method": method,
                    "multiplying_factor": consumed,
                    "emissions_kg": total_kg,
                    "emissions_tonnes": total_tonnes,
                    "source": asset.get("source", "Unknown"),
                    "source_year": asset.get("source_year", "Unknown")
                }
                results[year]["sources"].append(source_info)
            else:
                print(f"Categoria '{category}' non riconosciuta.")

    # Converti i risultati in un dizionario normale
    final_output = {}
    for year, data in results.items():
        final_output[year] = data.copy()
        # Aggiungi le tonnellate (già calcolate nelle funzioni di calcolo)
    return final_output

#############################
# 4) FUNZIONE PER STAMPARE I RISULTATI
#############################

def print_emissions_report(results: dict):
    """
    Stampa un report dettagliato delle emissioni raggruppate per anno,
    includendo le fonti delle emissioni.

    Args:
        results (dict): Emissioni raggruppate per anno.
    """
    print("Risultati calcolo Scope 2 (raggruppati per anno):")
    for year in sorted(results.keys()):
        data = results[year]
        print(f"\nAnno: {year}")
        print(f"  Purchased Electricity (kg): {data.get('purchased_electricity_kg', 0.0):.2f} | (ton): {data.get('purchased_electricity_kg', 0.0) / 1000:.2f}")
        print(f"  Purchased Heat or Steam (kg): {data.get('purchased_heat_or_steam_kg', 0.0):.2f} | (ton): {data.get('purchased_heat_or_steam_kg', 0.0) / 1000:.2f}")
        print(f"  Total Emissions (kg):         {data.get('total_kg', 0.0):.2f} | (ton): {data.get('total_kg', 0.0) / 1000:.2f}")

        # Stampa le fonti
        if data.get("sources"):
            print("  Fonti delle Emissioni:")
            for source in data["sources"]:
                print(
                    f"    - Asset: {source['asset_name']}, Categoria: {source['category']}, Metodo: {source['method']}, "
                    f"Quantità: {source['multiplying_factor']}, Emissioni: {source['emissions_kg']:.2f} kg "
                    f"({source['emissions_tonnes']:.2f} ton), Fonte: {source['source']}, Anno Fonte: {source['source_year']}"
                )

#############################
# 5) MAIN: ESEMPIO DI UTILIZZO
#############################

if __name__ == "__main__":
    # Esempio di session_id
    session_id = "my_session_scope1"

    # Calcola le emissioni
    emissions_results = compute_scope2_emissions(session_id)

    # Stampa il report
    print_emissions_report(emissions_results)

    # (Opzionale) Salva i risultati in un file JSON
    output_path = os.path.join(".", session_id, "scope2_emissions_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(emissions_results, f, indent=4)
    print(f"\nRisultati salvati in '{output_path}'")
