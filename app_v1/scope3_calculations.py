import json
import os
from collections import defaultdict


#############################
# 1) FUNZIONI DI CALCOLO SCOPE 3
#############################

# Categoria 1: Purchased Goods and Services
import json
import os
from collections import defaultdict

# Valori di riferimento standard
DEFAULT_SPEND = 1000.0  # EUR
DEFAULT_EMISSION_FACTOR = 0.0  # kg CO2e per unità di spesa
DEFAULT_QUANTITY = 1.0  # unità
DEFAULT_AVERAGE_EMISSION_FACTOR = 0.00  # kg CO2e per unità di quantità
DEFAULT_TRANSPORT_SPEND = 2000.0  # EUR
DEFAULT_DISTANCE = 100.0  # km
DEFAULT_MASS_OR_VOLUME = 50.0  # tonnellate o litri
DEFAULT_WASTE_AMOUNT = 300.0  # kg
DEFAULT_TRAVEL_SPEND = 1500.0  # EUR
DEFAULT_NIGHTS = 10  # notti
DEFAULT_DAILY_DISTANCE = 30.0  # km/giorno
DEFAULT_WORKING_DAYS_PER_YEAR = 220  # giorni
DEFAULT_FUEL_USED = 500.0  # litri o kg
DEFAULT_POWER_CONSUMPTION_KW = 5.0  # kW
DEFAULT_HEATING_POWER_KW = 3.0  # kW
DEFAULT_COOLING_POWER_KW = 4.0  # kW
DEFAULT_WORKING_DAYS = 220  # giorni
DEFAULT_TOTAL_FLOOR_SPACE = 1000.0  # m²
DEFAULT_LEASED_FLOOR_SPACE = 500.0  # m²
DEFAULT_MONTHS_LEASED = 12  # mesi
DEFAULT_DISTANCE_PER_YEAR = 200.0  # km

#############################
# 1) FUNZIONI DI CALCOLO SCOPE 3
#############################

# Categoria 1: Purchased Goods and Services
def calculate_purchased_goods_spend_based(data: dict) -> dict:
    spend = data.get("multiplying_factor", DEFAULT_SPEND)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = spend * ef
    return {
        "method": "spend_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_purchased_goods_supplier_specific(data: dict) -> dict:
    quantity = data.get("multiplying_factor", DEFAULT_QUANTITY)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = quantity * ef
    return {
        "method": "supplier_specific",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_purchased_goods_average_data(data: dict) -> dict:
    quantity = data.get("multiplying_factor", DEFAULT_QUANTITY)
    average_ef = data.get('emission_factor_kg', DEFAULT_AVERAGE_EMISSION_FACTOR)
    total_kg = quantity * average_ef
    return {
        "method": "average_data",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


# Categoria 2: Capital Goods
def calculate_capital_goods_spend_based(data: dict) -> dict:
    spend = data.get("multiplying_factor", DEFAULT_SPEND)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = spend * ef
    return {
        "method": "spend_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_capital_goods_supplier_specific(data: dict) -> dict:
    quantity = data.get("multiplying_factor", DEFAULT_QUANTITY)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = quantity * ef
    return {
        "method": "supplier_specific",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_capital_goods_average_data(data: dict) -> dict:
    quantity = data.get("multiplying_factor", DEFAULT_QUANTITY)
    average_ef = data.get('emission_factor_kg', DEFAULT_AVERAGE_EMISSION_FACTOR)
    total_kg = quantity * average_ef
    return {
        "method": "average_data",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


# Categoria 4: Upstream Transportation and Distribution
def calculate_upstream_transport_spend_based(data: dict) -> dict:
    spend = data.get("multiplying_factor", DEFAULT_TRANSPORT_SPEND)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = spend * ef
    return {
        "method": "spend_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_upstream_transport_distance_based(data: dict) -> dict:
    distance = data.get("multiplying_factor", DEFAULT_DISTANCE)
    mass = data.get("mass_or_volume", DEFAULT_MASS_OR_VOLUME)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = distance * mass * ef
    return {
        "method": "distance_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


# Categoria 5: Waste Generated in Operations
def calculate_waste_generated_by_type(data: dict) -> dict:
    amount = data.get("multiplying_factor", DEFAULT_WASTE_AMOUNT)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = amount * ef
    return {
        "method": "waste_type_method",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_waste_supplier_specific(data: dict) -> dict:
    amount = data.get("multiplying_factor", DEFAULT_WASTE_AMOUNT)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = amount * ef
    return {
        "method": "supplier_specific",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_waste_average_data(data: dict) -> dict:
    amount = data.get("multiplying_factor", DEFAULT_WASTE_AMOUNT)
    average_ef = data.get('emission_factor_kg', DEFAULT_AVERAGE_EMISSION_FACTOR)
    total_kg = amount * average_ef
    return {
        "method": "average_data",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


# Categoria 6: Business Travel
def calculate_business_travel_spend_based(data: dict) -> dict:
    spend = data.get("multiplying_factor", DEFAULT_TRAVEL_SPEND)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = spend * ef
    return {
        "method": "spend_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_business_travel_distance_based(data: dict) -> dict:
    distance = data.get("multiplying_factor", DEFAULT_DISTANCE)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = distance * ef
    return {
        "method": "distance_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_business_travel_accommodation(data: dict) -> dict:
    nights = data.get("multiplying_factor", DEFAULT_NIGHTS)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = nights * ef
    return {
        "method": "accommodation_location",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


# Categoria 7: Employee Commuting
def calculate_employee_commuting_distance_based(data: dict) -> dict:
    daily_distance = data.get("multiplying_factor", DEFAULT_DAILY_DISTANCE)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    days = data.get("working_days_per_year", DEFAULT_WORKING_DAYS_PER_YEAR)
    total_kg = daily_distance * ef * days
    return {
        "method": "transport_distance_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_employee_commuting_fuel_amount(data: dict) -> dict:
    fuel = data.get("multiplying_factor", DEFAULT_FUEL_USED)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = fuel * ef
    return {
        "method": "transport_fuel_amount",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_home_office_electricity_use(data: dict) -> dict:
    power_kW = data.get("power_consumption_kW", DEFAULT_POWER_CONSUMPTION_KW)
    hours = data.get("daily_hours", 8.0)  # Default a 8 ore/giorno
    days = data.get("working_days", DEFAULT_WORKING_DAYS)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kWh = power_kW * hours * days * data.get("multiplying_factor", 1)
    total_kg = total_kWh * ef
    return {
        "method": "home_office_electricity",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_home_office_heating(data: dict) -> dict:
    power_kW = data.get("heating_power_kW", DEFAULT_HEATING_POWER_KW)
    hours = data.get("daily_hours", 5.0)  # Default a 5 ore/giorno
    days = data.get("working_days", DEFAULT_WORKING_DAYS)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kWh = power_kW * hours * days * data.get("multiplying_factor", 1)
    total_kg = total_kWh * ef
    return {
        "method": "home_office_heating",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_home_office_cooling(data: dict) -> dict:
    power_kW = data.get("cooling_power_kW", DEFAULT_COOLING_POWER_KW)
    hours = data.get("daily_hours", 4.0)  # Default a 4 ore/giorno
    days = data.get("working_days", DEFAULT_WORKING_DAYS)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kWh = power_kW * hours * days * data.get("multiplying_factor", 1)
    total_kg = total_kWh * ef
    return {
        "method": "home_office_cooling",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


# Categoria 8: Upstream Leased Assets
def calculate_upstream_leased_building_asset_specific(data: dict) -> dict:
    scope1 = data.get("total_building_emissions_scope1_kg", 1000.0)  # Valore di riferimento
    scope2 = data.get("total_building_emissions_scope2_kg", 500.0)  # Valore di riferimento
    leased = data.get("leased_floor_space", DEFAULT_LEASED_FLOOR_SPACE)
    total_space = data.get("total_floor_space", DEFAULT_TOTAL_FLOOR_SPACE)
    months = data.get("months_leased", DEFAULT_MONTHS_LEASED)
    ratio = leased / total_space if total_space else 0
    ratio_per_year = ratio * (months / 12.0)
    total_emissions_building = scope1 + scope2
    total_kg = ratio_per_year * total_emissions_building
    return {
        "method": "leased_building_asset_specific",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_upstream_leased_building_average_data(data: dict) -> dict:
    average_ef = data.get('emission_factor_kg', DEFAULT_AVERAGE_EMISSION_FACTOR)
    space = data.get("leased_floor_space", DEFAULT_LEASED_FLOOR_SPACE)
    months = data.get("months_leased", DEFAULT_MONTHS_LEASED)
    ratio_year = months / 12.0
    total_kg = average_ef * space * ratio_year
    return {
        "method": "leased_building_average_data",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_upstream_leased_vehicles_fuel_amount(data: dict) -> dict:
    fuel = data.get("multiplying_factor", DEFAULT_FUEL_USED)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = fuel * ef
    return {
        "method": "leased_vehicles_fuel_amount",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_upstream_leased_vehicles_vehicle_type(data: dict) -> dict:
    distance = data.get("multiplying_factor", DEFAULT_DISTANCE_PER_YEAR)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = distance * ef
    return {
        "method": "leased_vehicles_vehicle_type",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


# Categoria 9: Downstream Transportation and Distribution
def calculate_downstream_transport_spend_based(data: dict) -> dict:
    spend = data.get("multiplying_factor", DEFAULT_TRANSPORT_SPEND)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = spend * ef
    return {
        "method": "spend_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


def calculate_downstream_transport_distance_based(data: dict) -> dict:
    distance = data.get("multiplying_factor", DEFAULT_DISTANCE)
    mass = data.get("mass", DEFAULT_MASS_OR_VOLUME)
    ef = data.get('emission_factor_kg', DEFAULT_EMISSION_FACTOR)
    total_kg = distance * mass * ef
    return {
        "method": "distance_based",
        "total_emissions_kg": total_kg,
        "total_emissions_tonnes": total_kg / 1000
    }


# Altre categorie possono essere aggiunte qui seguendo lo stesso schema

#############################
# 2) FUNZIONE PRINCIPALE PER CALCOLARE LE EMISSIONI SCOPE 3
#############################

def compute_scope3_emissions(session_id: str):
    """
    Legge i file JSON delle categorie Scope 3, applica le formule di calcolo,
    e restituisce un dizionario con le emissioni raggruppate per anno, includendo le fonti.
    """
    # Directory di salvataggio
    session_dir = os.path.join(".", session_id)

    # File di salvataggio per Scope 3
    SAVE_FILES = {
        "purchased-goods-and-services": "purchased_goods_services_assets_list.json",
        "capital-goods": "capital_goods_assets_list.json",
        "upstream-transportation-and-distribution": "upstream_transport_assets_list.json",
        "waste-generated-in-operations": "waste_generated_in_operations_assets_list.json",
        "business-travels": "business_travel_assets_list.json",
        "employee-commuting": "employee_commuting_assets_list.json",
        "upstream-leased-assets": "upstream_leased_assets_list.json",
        "downstream-transportation-and-distribution": "downstream_transport_assets_list.json"
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
    scope3_assets = {}
    for category, filename in SAVE_FILES.items():
        scope3_assets[category] = load_list_from_file(session_id, filename)

    # Dati finali raggruppati per anno
    results = defaultdict(lambda: {
        "purchased_goods_and_services_kg": 0.0,
        "capital_goods_kg": 0.0,
        "upstream_transportation_and_distribution_kg": 0.0,
        "waste_generated_in_operations_kg": 0.0,
        "business_travels_kg": 0.0,
        "employee_commuting_kg": 0.0,
        "upstream_leased_assets_kg": 0.0,
        "downstream_transportation_and_distribution_kg": 0.0,
        "total_kg": 0.0,
        "sources": []  # Aggiunto per tracciare le fonti
    })

    # Mappa categorie a funzioni di calcolo
    calculation_functions = {
        "purchased-goods-and-services": {
            "spend_based": calculate_purchased_goods_spend_based,
            "supplier_specific": calculate_purchased_goods_supplier_specific,
            "average_data": calculate_purchased_goods_average_data
        },
        "capital-goods": {
            "spend_based": calculate_capital_goods_spend_based,
            "supplier_specific": calculate_capital_goods_supplier_specific,
            "average_data": calculate_capital_goods_average_data
        },
        "upstream-transportation-and-distribution": {
            "spend_based": calculate_upstream_transport_spend_based,
            "distance_based": calculate_upstream_transport_distance_based
        },
        "waste-generated-in-operations": {
            "waste_type_method": calculate_waste_generated_by_type,
            "supplier_specific": calculate_waste_supplier_specific,
            "average_data": calculate_waste_average_data
        },
        "business-travels": {
            "spend_based": calculate_business_travel_spend_based,
            "distance_based": calculate_business_travel_distance_based,
            "accommodation_location": calculate_business_travel_accommodation
        },
        "employee-commuting": {
            "transport_distance_based": calculate_employee_commuting_distance_based,
            "transport_fuel_amount": calculate_employee_commuting_fuel_amount,
            "home_office_electricity": calculate_home_office_electricity_use,
            "home_office_heating": calculate_home_office_heating,
            "home_office_cooling": calculate_home_office_cooling
        },
        "upstream-leased-assets": {
            "leased_building_asset_specific": calculate_upstream_leased_building_asset_specific,
            "leased_building_average_data": calculate_upstream_leased_building_average_data,
            "leased_vehicles_fuel_amount": calculate_upstream_leased_vehicles_fuel_amount,
            "leased_vehicles_vehicle_type": calculate_upstream_leased_vehicles_vehicle_type
        },
        "downstream-transportation-and-distribution": {
            "spend_based": calculate_downstream_transport_spend_based,
            "distance_based": calculate_downstream_transport_distance_based
        }
        # Altre categorie possono essere aggiunte qui
    }

    # Itera su ogni categoria e calcola le emissioni
    for category, assets in scope3_assets.items():
        for asset in assets:
            year = asset.get("year", 2023)  # Default se mancante
            method = asset.get("method", "").lower()
            calc_funcs = calculation_functions.get(category, {})
            calc_func = calc_funcs.get(method, None)
            if calc_func:
                emission_result = calc_func(asset)
                emission_kg = emission_result.get("total_emissions_kg", 0.0)

                # Aggiorna i risultati per anno
                key = f"{category.replace('-', '_')}_kg"
                if key in results[year]:
                    results[year][key] += emission_kg
                else:
                    results[year][key] = emission_kg
                results[year]["total_kg"] += emission_kg

                # Aggiungi le informazioni sulla fonte, includendo il fattore moltiplicativo e la fonte
                source_info = {
                    "asset_name": asset.get("custom_asset_name", "Unknown"),
                    "category": category,
                    "method": method,
                    "multiplying_factor": asset.get("multiplying_factor", 0.0),
                    "emissions_kg": emission_kg,
                    "emissions_tonnes": emission_kg / 1000.0,
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
        # Aggiungi le tonnellate
        for key in data:
            if not key.endswith("_tonnes") and key != "sources":
                final_output[year][f"{key}_tonnes"] = data[key] / 1000

        # Le fonti sono già incluse come lista di dizionari
    return final_output


#############################
# 3) ESEMPIO DI UTILIZZO
#############################

if __name__ == "__main__":
    # Esempio di session_id
    session_id = "my_session_scope1"

    emissions = compute_scope3_emissions(session_id)

    # Stampa un report semplice
    print("Risultati calcolo Scope 3 (raggruppati per anno):")
    for year in sorted(emissions.keys()):
        data = emissions[year]
        print(f"\nAnno: {year}")
        print(
            f"  Purchased Goods and Services (kg): {data.get('purchased_goods_and_services_kg', 0.0):.2f} | (ton): {data.get('purchased_goods_and_services_kg_tonnes', 0.0):.2f}")
        print(
            f"  Capital Goods (kg): {data.get('capital_goods_kg', 0.0):.2f} | (ton): {data.get('capital_goods_kg_tonnes', 0.0):.2f}")
        print(
            f"  Upstream Transportation and Distribution (kg): {data.get('upstream_transportation_and_distribution_kg', 0.0):.2f} | (ton): {data.get('upstream_transportation_and_distribution_kg_tonnes', 0.0):.2f}")
        print(
            f"  Waste Generated in Operations (kg): {data.get('waste_generated_in_operations_kg', 0.0):.2f} | (ton): {data.get('waste_generated_in_operations_kg_tonnes', 0.0):.2f}")
        print(
            f"  Business Travels (kg): {data.get('business_travels_kg', 0.0):.2f} | (ton): {data.get('business_travels_kg_tonnes', 0.0):.2f}")
        print(
            f"  Employee Commuting (kg): {data.get('employee_commuting_kg', 0.0):.2f} | (ton): {data.get('employee_commuting_kg_tonnes', 0.0):.2f}")
        print(
            f"  Upstream Leased Assets (kg): {data.get('upstream_leased_assets_kg', 0.0):.2f} | (ton): {data.get('upstream_leased_assets_kg_tonnes', 0.0):.2f}")
        print(
            f"  Downstream Transportation and Distribution (kg): {data.get('downstream_transportation_and_distribution_kg', 0.0):.2f} | (ton): {data.get('downstream_transportation_and_distribution_kg_tonnes', 0.0):.2f}")
        print(
            f"  Total Emissions (kg): {data.get('total_kg', 0.0):.2f} | (ton): {data.get('total_kg_tonnes', 0.0):.2f}")

        # Stampa le fonti
        if data.get("sources"):
            print("  Fonti delle Emissioni:")
            for source in data["sources"]:
                print(
                    f"    - Asset: {source['asset_name']}, Categoria: {source['category']}, Metodo: {source['method']}, Quantità: {source['multiplying_factor']}, Emissioni: {source['emissions_kg']:.2f} kg ({source['emissions_tonnes']:.2f} ton), Fonte: {source['source']}, Anno Fonte: {source['source_year']}")
