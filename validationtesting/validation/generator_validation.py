"""
This module contains functions for validating the generator model.
"""

import streamlit as st
import pandas as pd
from config.path_manager import PathManager
import datetime

def get_efficiency_from_tabular(load: float, type_int: int) -> float:
    """Extract the efficiency from the tabular data for the specified load and generator type."""
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

def get_efficiency_from_formula(generator_energy: float, type: int) -> float:
    """Calculate the efficiency using the formula for the specified generator type."""
    # Get the formula for the specified generator type
    formula = st.session_state.generator_efficiency_formula[type]  # Example: "100 * (P / 20.0)"
    
    # Ensure `P` in the formula represents the generator power value
    try:
        # Replace 'P' with the actual generator power value
        efficiency = eval(formula.replace('P', str(generator_energy)))
        return efficiency
    except Exception as e:
        st.error(f"Error evaluating the formula '{formula}': {e}")
        return None


def test_power_limits(power: float, max_power: float, min_power: float) -> bool:
    """Test if the power is within the specified limits."""
    if power > max_power or power < min_power and power != 0:
        return False
    else: 
        return True

def temporal_degradation_efficiency(efficiency: float, degradation_rate: float, date: datetime.date, installation_date: datetime.date) -> float:
    """Adjust the efficiency based on temporal degradation."""
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

def get_fuel_consumption(energy: float, lhv: float, efficiency: float) -> float:
    """
    Calculate the fuel consumption for a generator based on its power, LHV, and efficiency.
    """

    # Energy input needed, accounting for efficiency
    energy_input = energy / efficiency

    # Fuel consumption in units
    fuel_consumption = energy_input / lhv

    return fuel_consumption
    
def generator_validation_testing() -> None:
    """Run the generator validation testing."""
    project_name = st.session_state.get("project_name")
    generator_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_generator.csv"
    generator_data = pd.read_csv(generator_data_path)

    # Print all current session states
    num_units = st.session_state.generator_num_units
    installation_dates = st.session_state.generator_installation_dates
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
    fuel_price = st.session_state.generator_fuel_price
    variable_fuel_price = st.session_state.generator_variable_fuel_price
    discount_rate = st.session_state.get("discount_rate") / 100
    start_date = st.session_state.get("start_date")

    if variable_fuel_price:
        fuel_price_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"generator_fuel_price.csv"
        fuel_price_df = pd.read_csv(fuel_price_path)


    generator_data['Benchmark Fuel Consumption generator Total [l]'] = 0
    generator_data['Benchmark Discounted Fuel Cost generator Total [$]'] = 0
    generator_data['Power Constraints Total'] = 0
    generator_data['Check Fuel Consumption Total'] = 0
    generator_data['Min Power'] = 0
    generator_data['Max Power'] = 0

    start_year = datetime.datetime.strptime(generator_data.iloc[0]['Time'], '%Y-%m-%d %H:%M:%S').year
    end_year = datetime.datetime.strptime(generator_data.iloc[-1]['Time'], '%Y-%m-%d %H:%M:%S').year
    number_of_years = (end_year - start_year) + 1  # +1 to include both start & end years
    progress_step = 1 / number_of_years
    st.write("--------------------")
    generator_progress = 0
    generator_progress_bar = st.progress(generator_progress)
    generator_text = st.empty()

    max_power = [0] * num_units
    min_power = [0] * num_units
    efficiency = [0] * num_units
    energy_this_generator = [0] * num_units
    for i, row in generator_data.iterrows():
        time = pd.to_datetime(row['Time'])
        if time.hour == 0 and time.month == 1 and time.day == 1:
            generator_progress += progress_step
            generator_progress_bar.progress(generator_progress)
            generator_text.write(f"Processing year {time.year} for generator validation")
        total_max_power = 0
        total_energy = row[f'Model generator Energy Total [Wh]']
        remaining_energy = total_energy
        for unit in range(num_units):
            type = int(generator_type[unit].replace("Type ", "")) - 1
            if installation_dates[unit] > time or installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[type]) < time:
                max_power[unit] = 0
                min_power[unit] = None
                unit_efficiency = 0
            else:
                max_power[unit] = max_powers[type]
                min_power[unit] = min_powers[type]
                if dynamic_efficiency:
                    energy_this_generator[unit] = min(remaining_energy, max_power[unit])
                    remaining_energy -= energy_this_generator[unit]
                    if dynamic_efficiency_type[type] == "Tabular Data":
                        unit_efficiency = get_efficiency_from_tabular(energy_this_generator[unit], type + 1)
                    else:
                        unit_efficiency = get_efficiency_from_formula(energy_this_generator[unit], type)
                else:
                    unit_efficiency = initial_efficiency[type]

            if temporal_degradation:
                unit_efficiency = temporal_degradation_efficiency(unit_efficiency, temporal_degradation_rate[type], time.date(), installation_dates[unit])

            efficiency[unit] = unit_efficiency
            total_max_power += max_power[unit]

        total_min_power = min(x for x in min_power if x is not None) if min_power else 0
        if not dynamic_efficiency:
            total_efficiency = sum(efficiency[unit] * max_power[unit] for unit in range(num_units)) / total_max_power
        else:
            total_efficiency = sum(efficiency[unit] * energy_this_generator[unit] for unit in range(num_units)) / total_energy
        generator_data.at[i, 'Min Power'] = total_min_power
        generator_data.at[i, 'Max Power'] = total_max_power
        generator_data.at[i, 'Power Constraints Total'] = test_power_limits(total_energy, total_max_power, total_min_power)
        generator_data.at[i, 'Benchmark Fuel Consumption generator Total [l]'] = get_fuel_consumption(total_energy, lhv[0], total_efficiency)

        if variable_fuel_price:
            try:
                fuel_price = fuel_price_df.loc[fuel_price_df['Year'] == time.year, 'Fuel Price [$/l]'].values[0]
            except KeyError:
                fuel_price = fuel_price_df['Fuel Price [$/l]'].iloc[-1]

        generator_data.at[i, 'Benchmark Discounted Fuel Cost generator Total [$]'] = \
            (generator_data.at[i, 'Benchmark Fuel Consumption generator Total [l]'] * fuel_price) / \
            ((1 + discount_rate) ** ((time.year - start_date.year) + 1))

    generator_text.write("Saving generator validation results...")
    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "generator_validation.csv"
    generator_data.to_csv(results_data_path)
    generator_text.write("Generator Benchmark Calculation Completed.")