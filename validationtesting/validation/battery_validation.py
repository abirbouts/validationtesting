"""
This module is used to validate the battery model output.
"""

import streamlit as st
import pandas as pd
import logging
from config.path_manager import PathManager
import datetime
import numpy as np
from blast import models

def test_charging_rate(battery_power: float, max_charge_power: float, max_discharge_power: float) -> bool:
    """Test if the battery power is within the charge and discharge power constraints."""
    return not (battery_power > max_discharge_power or (0 - battery_power) > max_charge_power)

def test_soc(battery_capacity: float, current_energy_stored: float, min_soc: float, max_soc: float) -> tuple:
    """Test if the battery state of charge is within the limits."""
    soc = current_energy_stored / battery_capacity
    is_within_limits = min_soc <= soc <= max_soc
    return soc, is_within_limits

def temporal_degradation_capacity(battery_capacity: float, degradation_rate: float, date: datetime.date, installation_date: datetime.date) -> float:
    """Calculate the battery capacity after temporal degradation."""
    years_since_install = (date - installation_date).days / 365.25
    return battery_capacity * (1 - degradation_rate * years_since_install)

def get_cyclic_degradation(cell, soc_values) -> float:
    """Calculate the battery state of health after cyclic degradation."""
    def prepare_input(soc_values):
        # Generate cumulative time in seconds (1 hour = 3600 seconds)
        time_seconds = np.array([i * 3600 for i in range(len(soc_values))], dtype=float)
        # Normalize SOC to range 0-1 (percentage to fraction)
        soc = np.clip(soc_values, 0, 1)
        # Constant temperature array (25°C for each time step)
        temperature_c = np.full(len(soc_values), 25, dtype=float)
        # Return the input dictionary
        return {
            "Time_s": time_seconds,
            "SOC": soc,
            "Temperature_C": temperature_c,
        }
    input_data = prepare_input(soc_values)
    # Simulate degradation for the current hour
    cell.simulate_battery_life(input_data)

    # Collect end-of-day results
    outputs = cell.outputs
    soh_end = outputs['q'][-1]  # Remaining capacity (SoH)

    return soh_end

def battery_validation_testing() -> None:
    """Run the battery validation testing."""
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
    end_of_life = [installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[unit]) for unit in range(num_units)]
    battery_type = st.session_state.battery_type
    initial_battery_capacity = st.session_state.battery_capacity
    initial_soc = [x / 100 for x in st.session_state.battery_initial_soc]
    charging_efficiency = [x / 100 for x in st.session_state.battery_charging_efficiency]
    discharging_efficiency = [x / 100 for x in st.session_state.battery_discharging_efficiency]
    inverter_efficiency = [x / 100 for x in st.session_state.battery_inverter_efficiency]
    min_soc = [x / 100 for x in st.session_state.battery_min_soc]
    max_soc = [x / 100 for x in st.session_state.battery_max_soc]
    temporal_degradation_rate = [x / 100 for x in st.session_state.battery_temporal_degradation_rate]
    cyclic_degradation = st.session_state.battery_cyclic_degradation
    discount_rate = st.session_state.get("discount_rate") / 100
    start_date = st.session_state.get("start_date")

    if scope == "Per Unit":
        for unit in range(num_units):
            battery_data[f"Model battery Discounted Energy Unit {unit+1} [Wh]"] = None
            battery_data[f"Energy Stored {unit+1} [Wh]"] = None
            battery_data[f"Capacity {unit+1}"] = None
            battery_data[f"Benchmark battery SoC Unit {unit+1} [%]"] = None
            battery_data[f"Charge Power Constraints Unit {unit+1}"] = None 
            battery_data[f"SoC Constraints Unit {unit+1}"] = None
        battery_data[f"Model battery Discounted Energy Total [Wh]"] = 0
    else:
        battery_data[f"Charge Power Constraints Total"] = None 
        battery_data[f"SoC Constraints Total"] = None
        battery_data[f"Energy Stored Total [Wh]"] = None
        battery_data[f"Capacity Total"] = None
        battery_data[f"Benchmark battery SoC Total [%]"] = None
        battery_data[f"Model battery Discounted Energy Total [Wh]"] = None
    battery_data['UTC Time'] = pd.to_datetime(battery_data['UTC Time'], errors='coerce')
    daily_data = battery_data.groupby(battery_data['UTC Time'].dt.date)
    
    if scope == "Per Unit":
        for unit in range(num_units):  # Loop through each unit first
            type = int(battery_type[unit].replace("Type ", "")) - 1
            
            # Initialize unit-specific values
            current_energy_stored = initial_soc[type] * initial_battery_capacity[type]
            battery_capacity = initial_battery_capacity[type]
            
            for day, group in daily_data:  # Loop through each day

                if st.session_state.battery_temporal_degradation:
                    battery_capacity = temporal_degradation_capacity(
                        initial_battery_capacity[type],
                        temporal_degradation_rate[type],
                        day,
                        installation_dates[unit]
                    )  
                if cyclic_degradation:
                    if day == list(daily_data.groups.keys())[0]:
                        model_name = st.session_state.battery_model[type]
                        model_class = getattr(models, model_name)
                        cell = model_class()
                    else:
                        soh = get_cyclic_degradation(cell, soc_values)
                        battery_capacity = soh * initial_battery_capacity[type]

                soc_values = []

                for i, row in group.iterrows():  # Loop through time steps
                    time = row['UTC Time']

                    # Check if the unit is within installation and end-of-life dates
                    if not installation_dates[unit] <= time <= end_of_life[unit]:
                        max_charge_power = 0
                        max_discharge_power = 0
                    else:
                        max_charge_power = max_charge_powers[type]
                        max_discharge_power = max_discharge_powers[type]

                    # Get the battery power for this unit
                    battery_power = row[f'Model battery Energy Unit {unit + 1} [Wh]']

                    # Update energy storage considering inverter efficiency
                    if st.session_state.battery_inverter_eff_included:
                        if battery_power <= 0:
                            current_energy_stored -= battery_power * charging_efficiency[type]
                        else:
                            current_energy_stored -= battery_power / discharging_efficiency[type]

                    # Update the battery data for this unit and time
                    battery_data.at[i, f"Charge Power Constraints Unit {unit+1}"] = test_charging_rate(
                        battery_power, max_charge_power, max_discharge_power
                    )
                    soc_value, battery_data.at[i, f"SoC Constraints Unit {unit+1}"] = test_soc(battery_capacity, current_energy_stored, min_soc[type], max_soc[type])
                    soc_values.append(soc_value)
                    battery_data.at[i, f"Benchmark battery SoC Unit {unit+1} [%]"] = soc_value
                    battery_data.at[i, f"Capacity {unit+1}"] = battery_capacity
                    battery_data.at[i, f"Energy Stored {unit+1} [Wh]"] = current_energy_stored
                    
                    # Calculate and update discounted energy
                    discounted_energy = battery_power / ((1 + discount_rate) ** ((time - start_date).days / 365))
                    battery_data.at[i, f"Model battery Discounted Energy Unit {unit+1} [Wh]"] = discounted_energy
                    battery_data.at[i, f"Model battery Discounted Energy Total [Wh]"] += discounted_energy

    if scope == "Total":
        charging_efficiencies = num_units * [0]
        discharging_efficiencies = num_units * [0]
        battery_capacities = num_units * [0]
        for i, row in battery_data.iterrows():
            total_max_charge_power = 0
            total_max_discharge_power = 0
            total_battery_capacity = 0
            time = row['UTC Time']
            for unit in range(num_units):
                type = int(battery_type[unit].replace("Type ", "")) - 1

                if i == 0:
                    current_energy_stored = initial_soc[type] * initial_battery_capacity[type]
                    battery_capacity = initial_battery_capacity[type]

                if st.session_state.battery_temporal_degradation:
                    battery_capacity = temporal_degradation_capacity(initial_battery_capacity[type], temporal_degradation_rate[type], time.date(), installation_dates[unit])
                
                if not installation_dates[unit] <= time <= end_of_life[unit]:
                    max_charge_power = 0
                    max_discharge_power = 0
                    battery_capacity = 0
                else:
                    max_charge_power = max_charge_powers[type]
                    max_discharge_power = max_discharge_powers[type]                

                total_max_charge_power += max_charge_power
                total_max_discharge_power += max_discharge_power
                total_battery_capacity += battery_capacity
                charging_efficiencies[unit] = charging_efficiency[type]
                discharging_efficiencies[unit] = discharging_efficiency[type]
                battery_capacities[unit] = battery_capacity

            total_charging_efficiency = sum(charging_efficiencies[unit] * battery_capacities[unit] for unit in range(num_units)) / total_battery_capacity
            total_discharging_efficiency = sum(discharging_efficiencies[unit] * battery_capacities[unit] for unit in range(num_units)) / total_battery_capacity
            min_soc_total = sum(min_soc[unit] * battery_capacities[unit] for unit in range(num_units)) / total_battery_capacity
            max_soc_total = sum(max_soc[unit] * battery_capacities[unit] for unit in range(num_units)) / total_battery_capacity
            battery_power = row[f'Model battery Energy Total [Wh]']
            if st.session_state.battery_inverter_eff_included:
                if battery_power <= 0:
                    current_energy_stored -= battery_power * total_charging_efficiency
                else:
                    current_energy_stored -= battery_power / total_discharging_efficiency


            battery_data.at[i, f"Charge Power Constraints Total"] = test_charging_rate(battery_power, total_max_charge_power, total_max_discharge_power)
            battery_data.at[i, f"Benchmark battery SoC Total [%]"], battery_data.loc[i, f"SoC Constraints Total"] = test_soc(total_battery_capacity, current_energy_stored, min_soc_total, max_soc_total)
            battery_data.at[i, f"Energy Stored Total [Wh]"] = current_energy_stored
            battery_data.at[i, f"Capacity Total"] = total_battery_capacity
            battery_data.at[i, f"Model battery Discounted Energy Total [Wh]"] = battery_power / ((1 + discount_rate) ** ((time - start_date).days / 365))

    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "battery_validation.csv"
    battery_data.to_csv(results_data_path)