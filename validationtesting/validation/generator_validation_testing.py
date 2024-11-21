import streamlit as st
import pandas as pd
import logging
from config.path_manager import PathManager
import datetime

def get_efficiency_from_tabular(load: float, type_int: int) -> float:
    project_name = st.session_state.get("project_name")
    dynamic_efficiency_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"generator_dynamic_efficiency_type_{type_int}.csv"
    
    # Load the efficiency data from the CSV
    efficiency_df = pd.read_csv(dynamic_efficiency_path)
    
    # If the load is exactly in the table, return the associated efficiency
    if load in efficiency_df['Load'].values:
        return efficiency_df.loc[efficiency_df['Load'] == load, 'Efficiency (%)'].iloc[0]
    
    # Find the next smaller and next bigger loads
    smaller_loads = efficiency_df[efficiency_df['Load'] < load]
    bigger_loads = efficiency_df[efficiency_df['Load'] > load]
    
    # Handle edge cases where load is outside the range of the table
    if smaller_loads.empty:
        return bigger_loads['Efficiency (%)'].iloc[0]  # Return the first (smallest) efficiency
    if bigger_loads.empty:
        return smaller_loads['Efficiency (%)'].iloc[-1]  # Return the last (largest) efficiency
    
    # Get the nearest smaller and bigger loads and their efficiencies
    load_low = smaller_loads['Load'].iloc[-1]
    load_high = bigger_loads['Load'].iloc[0]
    efficiency_low = smaller_loads['Efficiency (%)'].iloc[-1]
    efficiency_high = bigger_loads['Efficiency (%)'].iloc[0]
    
    # Perform linear interpolation
    interpolated_efficiency = efficiency_low + (efficiency_high - efficiency_low) * ((load - load_low) / (load_high - load_low))
    
    return interpolated_efficiency

def get_efficiency_from_formula(generator_power: float, type_int: int) -> float:
    # Get the formula for the specified generator type
    formula = st.session_state.generator_efficiency_formula[type_int - 1]  # Example: "100 * (P / 20.0)"
    
    # Ensure `P` in the formula represents the generator power value
    try:
        # Replace 'P' with the actual generator power value
        efficiency = eval(formula.replace('P', str(generator_power)))
        return efficiency
    except Exception as e:
        st.error(f"Error evaluating the formula '{formula}': {e}")
        return None


def test_power_limits(power: float, max_power: float, min_power: float) -> bool:
    if power > max_power or power < min_power:
        return False
    else: 
        return True

def temporal_degradation_efficiency(efficiency: float, degradation_rate: float, date: datetime.date, installation_date: datetime.date) -> float:
    def get_years_since_install(installation_date: datetime.date, current_date: datetime.date) -> float:
        # Ensure both are 'date' objects
        installation_date = installation_date.date()
        
        # Calculate the difference in days and convert to years
        days_since_install = (current_date - installation_date).days
        years_since_install = days_since_install / 365.25
        return years_since_install
        
    years_installed = get_years_since_install(installation_date, date)
    efficiency = efficiency * (1 - (degradation_rate) * years_installed)
    return efficiency

def get_fuel_consumption(power: float, lhv: float, efficiency: float) -> float:
    """
    Calculate the fuel consumption for a generator based on its power, LHV, and efficiency.

    Args:
    - generator_power_kw (float): Power output of the generator in kW.
    - lhv_kwh_per_unit (float): Lower Heating Value of the fuel in kWh per unit (e.g., kWh/liter for diesel).
    - efficiency (float): Efficiency of the generator as a decimal (e.g., 0.35 for 35% efficiency).
    - operating_hours (float): Number of hours the generator is running (default is 1 hour).

    Returns:
    - fuel_consumption (float): Fuel consumption in units (e.g., liters).
    """
    if efficiency <= 0 or efficiency > 1:
        raise ValueError("Efficiency must be a decimal between 0 and 1.")

    # Energy input needed, accounting for efficiency
    energy_input = power / efficiency

    # Fuel consumption in units
    fuel_consumption = energy_input / lhv

    return fuel_consumption
    
def generator_validation_testing() -> None:
    logging.info('Running generator validation testing')
    project_name = st.session_state.get("project_name")
    generator_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_generator.csv"
    generator_data = pd.read_csv(generator_data_path)

    num_units = st.session_state.generator_num_units
    scope = st.session_state.generator_model_output_scope
    installation_dates = st.session_state.generator_installation_dates_utc
    lifetime = st.session_state.generator_lifetime
    generator_type = st.session_state.generator_type
    dynamic_efficiency = st.session_state.generator_dynamic_efficiency
    dynamic_efficiency_type = st.session_state.generator_dynamic_efficiency_type
    temporal_degradation = st.session_state.generator_temporal_degradation
    initial_efficiency = [x / 100 for x in st.session_state.generator_efficiency]
    min_powers = st.session_state.generator_min_power
    max_powers = st.session_state.generator_max_power
    lhv = st.session_state.generator_fuel_lhv
    temporal_degradation_rate = [x / 100 for x in st.session_state.battery_temporal_degradation_rate]

    if scope == "Per Unit":
        for unit in range(num_units):
            generator_data[f'Benchmark Fuel Consumption Generator Unit {unit + 1}'] = None
            generator_data[f"Power Constraints Unit {unit+1}"] = None 
            generator_data[f"Check Fuel Consumption Unit {unit+1}"] = None
    else:
        pass
    if scope == "Per Unit":
        for unit in range(num_units):
            for i in range(0, len(generator_data)):
                time = generator_data['UTC Time'][i]
                time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                type = generator_type[unit]
                type_int = int(type.replace("Type ", ""))
                if installation_dates[unit] > time or installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[type_int-1]) < time:
                    max_power = 0
                    min_power = 0
                else:
                    max_power = max_powers[type_int-1]
                    min_power = min_powers[type_int-1]
                generator_power = generator_data[f'Model generator Power Unit {unit + 1}'][i]
                if dynamic_efficiency:
                    if dynamic_efficiency_type[type_int-1] == "Tabular Data":
                        efficiency = get_efficiency_from_tabular(generator_power, type_int)
                    else:
                        efficiency = get_efficiency_from_formula(generator_power, type_int)
                else:
                    efficiency = initial_efficiency[type_int-1]
                if temporal_degradation:
                    efficiency = temporal_degradation_efficiency(efficiency, temporal_degradation_rate[type_int-1], time.date(), installation_dates[unit])
                else:
                    efficiency = initial_efficiency[type_int-1]
                generator_data[f"Power Constraints Unit {unit+1}"][i] = test_power_limits(generator_power, max_power, min_power)
                generator_data[f'Benchmark Fuel Consumption Generator Unit {unit + 1}'][i] = get_fuel_consumption(generator_power, lhv, efficiency)
                generator_data[f"Check Fuel Consumption Unit {unit+1}"][i] = (abs(((generator_data[f'Model Fuel Consumption Unit {unit + 1}'][i]-generator_data[f'Benchmark Fuel Consumption Generator Unit {unit + 1}'][i])/generator_data[f'Benchmark Fuel Consumption Generator Unit {unit + 1}'][i])) < 0.01)
            false_count_power_constraints = (generator_data[f"Power Constraints Unit {unit+1}"] == False).sum()
            false_count_fuel_consumption = (generator_data[f"Check Fuel Consumption Unit {unit+1}"] == False).sum()
            logging.info(f'For Unit {unit+1} there are {false_count_power_constraints} (out of {len(generator_data)}) timestamps where the power was not in boundaries (minimum and maximum power)')
            logging.info(f'For Unit {unit+1} the fuel consumption does not match the energy output for {false_count_fuel_consumption} (out of {len(generator_data)}) timestamps')
  
    else:
        pass

    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "generator_validation.csv"
    generator_data.to_csv(results_data_path)