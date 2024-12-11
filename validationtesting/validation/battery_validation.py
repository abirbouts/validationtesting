import streamlit as st
import pandas as pd
import logging
from config.path_manager import PathManager
import datetime


def test_charging_rate(battery_power: float, max_charge_power: float, max_discharge_power: float) -> bool:
    if battery_power > max_discharge_power or (0 - battery_power) > max_charge_power:
        return False
    else:
        return True
    
def test_soc(battery_capacity: float, current_energy_stored: float, min_soc: float, max_soc: float) -> tuple:
    # Check SoC with respect to effective capacity
    soc = (current_energy_stored / battery_capacity)  # SoC as a percentage of current effective capacity
    # Apply SoC limits
    if soc > max_soc:
        return soc, False
    elif soc < min_soc:
        return soc, False
    else:
        return soc, True

def temporal_degradation_capacity(battery_capacity: float, degradation_rate: float, date: datetime.date, installation_date: datetime.date) -> float:
    def get_years_since_install(installation_date: datetime.date, current_date: datetime.date) -> float:
        # Ensure both are 'date' objects
        installation_date = installation_date.date()
        
        # Calculate the difference in days and convert to years
        days_since_install = (current_date - installation_date).days
        years_since_install = days_since_install / 365.25
        return years_since_install
        
    years_installed = get_years_since_install(installation_date, date)
    battery_capacity = battery_capacity * (1 - (degradation_rate) * years_installed)
    return battery_capacity
    
def battery_validation_testing() -> None:
    logging.info('Running battery validation testing')
    project_name = st.session_state.get("project_name")
    battery_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_battery.csv"
    battery_data = pd.read_csv(battery_data_path)

    num_units = st.session_state.battery_num_units
    scope = st.session_state.battery_model_output_scope
    max_charge_powers = st.session_state.battery_max_charge_power
    max_discharge_powers = st.session_state.battery_max_discharge_power
    installation_dates = st.session_state.battery_installation_dates_utc
    lifetime = st.session_state.battery_lifetime
    battery_type = st.session_state.battery_type
    initial_battery_capacity = st.session_state.battery_capacity
    initial_soc = [x / 100 for x in st.session_state.battery_initial_soc]
    charging_efficiency = [x / 100 for x in st.session_state.battery_charging_efficiency]
    discharging_efficiency = [x / 100 for x in st.session_state.battery_discharging_efficiency]
    inverter_efficiency = [x / 100 for x in st.session_state.battery_inverter_efficiency]
    min_soc = [x / 100 for x in st.session_state.battery_min_soc]
    max_soc = [x / 100 for x in st.session_state.battery_max_soc]
    inverter_efficiency = [x / 100 for x in st.session_state.battery_inverter_efficiency]
    temporal_degradation_rate = [x / 100 for x in st.session_state.battery_temporal_degradation_rate]
    discount_rate = st.session_state.get("discount_rate") / 100
    start_date = st.session_state.get("start_date")
    
    if scope == "Per Unit":
        for unit in range(num_units):
            battery_data[f"Model battery Discounted Energy Unit {unit+1} [Wh]"] = None
            battery_data[f"Energy Stored {unit+1} [Wh]"] = None
            battery_data[f"Capacity {unit+1}"] = None
            battery_data[f"SoC Unit {unit+1}"] = None
            battery_data[f"Charge Power Constraints Unit {unit+1}"] = None 
            battery_data[f"SoC Constraints Unit {unit+1}"] = None
        battery_data[f"Model battery Discounted Energy Total [Wh]"] = 0
    else:
        battery_data[f"Charge_Power_Constraints_Total"] = None 
        battery_data[f"SoC Constraints Unit Total"] = None
    if scope == "Per Unit":
        for unit in range(num_units):
            for i in range(0, len(battery_data)):
                time = battery_data.loc[i, 'UTC Time']
                time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                type = battery_type[unit]
                type_int = int(type.replace("Type ", ""))
                if installation_dates[unit] > time or installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[type_int-1]) < time:
                    max_charge_power = 0
                    max_discharge_power = 0
                else:
                    max_charge_power = max_charge_powers[type_int-1]
                    max_discharge_power = max_discharge_powers[type_int-1]
                battery_power = battery_data.loc[i, f'Model battery Energy Unit {unit + 1} [Wh]']
                battery_data.loc[i, f"Model battery Discounted Energy Unit {unit+1} [Wh]"] = battery_power / ((1 + discount_rate) ** ((time - start_date).days / 365))
                battery_data.loc[i, f"Model battery Discounted Energy Total [Wh]"] += battery_data.loc[i, f"Model battery Discounted Energy Unit {unit+1} [Wh]"]
                if i == 0:
                    current_energy_stored = initial_soc[type_int-1] * initial_battery_capacity[type_int-1]
                    battery_capacity = initial_battery_capacity[type_int-1]
                if st.session_state.battery_inverter_eff_included:
                    if battery_power <= 0:
                        current_energy_stored -= battery_power * charging_efficiency[type_int-1]
                    else:
                        current_energy_stored -= battery_power / (discharging_efficiency[type_int-1])
                if st.session_state.battery_temporal_degradation:
                    battery_capacity = temporal_degradation_capacity(initial_battery_capacity[type_int-1], temporal_degradation_rate[type_int-1], time.date(), installation_dates[unit])
                battery_data.loc[i, f"Charge Power Constraints Unit {unit+1}"] = test_charging_rate(battery_power, max_charge_power, max_discharge_power)
                battery_data.loc[i, f"SoC Unit {unit+1}"], battery_data.loc[i, f"SoC Constraints Unit {unit+1}"] = test_soc(battery_capacity, current_energy_stored, min_soc[type_int-1], max_soc[type_int-1])
                battery_data.loc[i, f"Capacity {unit+1}"] = battery_capacity
                battery_data.loc[i, f"Energy Stored {unit+1} [Wh]"] = current_energy_stored
            false_count = (battery_data[f"Charge Power Constraints Unit {unit+1}"] == False).sum()
            false_count_soc = (battery_data[f"SoC Constraints Unit {unit+1}"] == False).sum()
            logging.info(f'For Unit {unit+1} there are {false_count} (out of {len(battery_data)}) timestamps where the charging power exceeded either the charging or discharging power limit')
            logging.info(f'For Unit {unit+1} there are {false_count_soc} (out of {len(battery_data)}) timestamps where the SoC is invalid')

    else:
        for unit in range(num_units):
            if installation_dates[unit] > time or installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[unit]) < time:
                max_charge_power += 0
                max_discharge_power += 0
            else:
                max_charge_power += max_charge_powers[unit]
                max_discharge_power += max_discharge_powers[unit]
        battery_power = battery_data.loc[i, f'Model battery Energy Total [Wh]']
        battery_data.loc[i, f"Charge Power Constraints Total"] = test_charging_rate(battery_power, max_charge_power, max_discharge_power)

    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "battery_validation.csv"
    battery_data.to_csv(results_data_path)