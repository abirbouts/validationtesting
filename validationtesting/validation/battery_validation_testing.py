import streamlit as st
import pandas as pd
import logging
from config.path_manager import PathManager
import datetime


def test_charging_rate(battery_power, max_charge_power, max_discharge_power):
    if battery_power > max_discharge_power or (0-battery_power) > max_charge_power:
        return False
    else: 
        return True
    
def test_soc(battery_capacity, current_energy_stored, min_soc, max_soc):
    # Check SoC with respect to effective capacity
    soc = (current_energy_stored / battery_capacity)  # SoC as a percentage of current effective capacity
    # Apply SoC limits
    if soc > max_soc:
        return False
    elif soc < min_soc:
        return False
    else:
        return True

def battery_validation_testing():
    logging.info('running battery validation testing')
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
    battery_capacity = st.session_state.battery_capacity
    initial_soc = [x / 100 for x in st.session_state.battery_initial_soc]
    charging_efficiency = [x / 100 for x in st.session_state.battery_charging_efficiency]
    discharging_efficiency = [x / 100 for x in st.session_state.battery_discharging_efficiency]
    inverter_efficiency = [x / 100 for x in st.session_state.battery_inverter_efficiency]
    min_soc = [x / 100 for x in st.session_state.battery_min_soc]
    max_soc = [x / 100 for x in st.session_state.battery_max_soc]

    if scope == "Per Unit":
        for unit in range(num_units):
            battery_data[f"Charge_Power_Constraints_Unit_{unit+1}"] = None 
            battery_data[f"SoC_Constraints_Unit_{unit+1}"] = None
    else:
        battery_data[f"Charge_Power_Constraints_Total"] = None 
        battery_data[f"SoC_Constraints_Unit_Total"] = None
    if scope == "Per Unit":
        for unit in range(num_units):
            for i in range(0, len(battery_data)):
                time = battery_data['UTC Time'][i]
                time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                type = battery_type[unit]
                type_int = int(type.replace("Type ", ""))
                if installation_dates[unit] > time or installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[type_int-1]) < time:
                    max_charge_power = 0
                    max_discharge_power = 0
                else:
                    max_charge_power = max_charge_powers[type_int-1]
                    max_discharge_power = max_discharge_powers[type_int-1]

                battery_power = battery_data[f'Model battery Power Unit {unit + 1}'][i]
                if i == 0:
                    current_energy_stored = initial_soc[type_int-1] * battery_capacity[type_int-1]
                if battery_power <= 0:
                    current_energy_stored -= battery_power * charging_efficiency[type_int-1] * inverter_efficiency[type_int-1]
                else:
                    current_energy_stored -= battery_power / (discharging_efficiency[type_int-1] * inverter_efficiency[type_int-1])
                battery_data[f"Charge_Power_Constraints_Unit_{unit+1}"][i] = test_charging_rate(battery_power, max_charge_power, max_discharge_power)
                battery_data[f"SoC_Constraints_Unit_{unit+1}"][i] = test_soc(battery_capacity, current_energy_stored, min_soc[type_int-1], max_soc[type_int-1])
            false_count = (battery_data[f"Charge_Power_Constraints_Unit_{unit+1}"] == False).sum()
            false_count_soc = (battery_data[f"SoC_Constraints_Unit_{unit+1}"] == False).sum()
            logging.info(f'For Unit {unit+1} there are {false_count} timestamps where the charging power exceeded either the charging or discharging power limit')
            logging.info(f'For Unit {unit+1} there are {false_count_soc} timestamps where the SoC is invalid')
  
    else:
        for unit in range(num_units):
            if installation_dates[unit] > time or installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[unit]) < time:
                max_charge_power += 0
                max_discharge_power += 0
            else:
                max_charge_power += max_charge_powers[unit]
                max_discharge_power += max_discharge_powers[unit]
        battery_power = battery_data[f'Model battery Power Total'][i]
        battery_data[f"Charge_Power_Constraints_Total"][i] = test_charging_rate(battery_power, max_charge_power, max_discharge_power)

    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "battery_validation.csv"
    battery_data.to_csv(results_data_path)