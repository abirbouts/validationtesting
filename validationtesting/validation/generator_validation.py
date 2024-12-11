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

def get_efficiency_from_formula(generator_energy: float, type_int: int) -> float:
    # Get the formula for the specified generator type
    formula = st.session_state.generator_efficiency_formula[type_int - 1]  # Example: "100 * (P / 20.0)"
    
    # Ensure `P` in the formula represents the generator power value
    try:
        # Replace 'P' with the actual generator power value
        efficiency = eval(formula.replace('P', str(generator_energy)))
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

def get_fuel_consumption(energy: float, lhv: float, efficiency: float) -> float:
    """
    Calculate the fuel consumption for a generator based on its power, LHV, and efficiency.

    Args:
    - generator_power_kw (float): Energy output of the generator in kWh.
    - lhv_kwh_per_unit (float): Lower Heating Value of the fuel in kWh per unit (e.g., kWh/liter for diesel).
    - efficiency (float): Efficiency of the generator as a decimal (e.g., 0.35 for 35% efficiency).
    - operating_hours (float): Number of hours the generator is running (default is 1 hour).

    Returns:
    - fuel_consumption (float): Fuel consumption in units (e.g., liters).
    """

    # Energy input needed, accounting for efficiency
    energy_input = energy / efficiency

    # Fuel consumption in units
    fuel_consumption = energy_input / lhv

    return fuel_consumption
    
def generator_validation_testing() -> None:
    logging.info('Running generator validation testing')
    project_name = st.session_state.get("project_name")
    generator_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_generator.csv"
    generator_data = pd.read_csv(generator_data_path)

    # Print all current session states
    st.session_state.generator_fuel_consumption_scope = ["Total"]
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
    fuel_consumption_scope = st.session_state.generator_fuel_consumption_scope
    model_fuel_consumption = st.session_state.generator_total_fuel_consumption
    fuel_price = st.session_state.generator_fuel_price
    variable_fuel_price = st.session_state.generator_variable_fuel_price
    variable_fuel_price_uploaded = st.session_state.generator_variable_fuel_price_uploaded
    discount_rate = st.session_state.get("discount_rate") / 100
    start_date = st.session_state.get("start_date")

    if variable_fuel_price:
        fuel_price_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"generator_fuel_price.csv"
        fuel_price_df = pd.read_csv(fuel_price_path)


    if scope == "Per Unit":
        for unit in range(num_units):
            generator_data[f'Model generator Discounted Energy Unit {unit + 1} [Wh]'] = None
            generator_data[f'Benchmark Fuel Consumption generator Unit {unit + 1} [l]'] = None
            generator_data[f'Benchmark Discounted Fuel Cost generator Unit {unit + 1} [$]'] = None
            generator_data[f"Power Constraints Unit {unit+1}"] = None 
            generator_data[f"Check Fuel Consumption Unit {unit+1}"] = None
    generator_data['Model generator Discounted Energy Total [Wh]'] = 0
    generator_data['Benchmark Fuel Consumption generator Total [l]'] = 0
    generator_data['Benchmark Discounted Fuel Cost generator Total [$]'] = 0
    generator_data['Power Constraints Total'] = 0
    generator_data['Check Fuel Consumption Total'] = 0
    logging.info(scope)
    if scope == "Per Unit":
        for unit in range(num_units):
            for i in range(0, len(generator_data)):
                time = generator_data.loc[i, 'UTC Time']
                time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                type = generator_type[unit]
                type_int = int(type.replace("Type ", ""))
                if installation_dates[unit] > time or installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[type_int-1]) < time:
                    max_power = 0
                    min_power = 0
                else:
                    max_power = max_powers[type_int-1]
                    min_power = min_powers[type_int-1]
                generator_energy = generator_data.loc[i, f'Model generator Energy Unit {unit + 1} [Wh]']
                generator_data.loc[i, f'Model generator Discounted Energy Unit {unit + 1} [Wh]'] = generator_energy / ((1 + discount_rate) ** ((time - start_date).days / 365))
                generator_data.loc[i, 'Model generator Discounted Energy Total [Wh]'] += generator_data.loc[i, f'Model generator Discounted Energy Unit {unit + 1} [Wh]'] 
                if dynamic_efficiency:
                    if dynamic_efficiency_type[type_int-1] == "Tabular Data":
                        efficiency = get_efficiency_from_tabular(generator_energy, type_int)
                    else:
                        efficiency = get_efficiency_from_formula(generator_energy, type_int)
                else:
                    efficiency = initial_efficiency[type_int-1]
                if temporal_degradation:
                    efficiency = temporal_degradation_efficiency(efficiency, temporal_degradation_rate[type_int-1], time.date(), installation_dates[unit])
                else:
                    efficiency = initial_efficiency[type_int-1]
                if variable_fuel_price:
                    try:
                        fuel_price = fuel_price_df.loc[fuel_price_df['Year'] == time.year, 'Fuel Price [$/l]'].values[0]
                    except:
                        try:
                            fuel_price = fuel_price_df.loc[fuel_price_df['Year'] == time.year - 1, 'Fuel Price [$/l]'].values[0]
                        except:
                            fuel_price = fuel_price_df.loc[fuel_price_df['Year'] == time.year + 1, 'Fuel Price [$/l]'].values[0]
                generator_data.loc[i, f"Power Constraints Unit {unit+1}"] = test_power_limits(generator_energy, max_power, min_power)
                fuel_consumption = get_fuel_consumption(generator_energy, lhv, efficiency)
                generator_data.loc[i, f'Benchmark Fuel Consumption generator Unit {unit + 1} [l]'] = fuel_consumption
                generator_data.loc[i, f'Benchmark Fuel Consumption generator Total [l]'] += fuel_consumption
                generator_data.loc[i, f'Benchmark Discounted Fuel Cost generator Unit {unit + 1} [$]'] = (fuel_consumption * fuel_price) / ((1 + discount_rate) ** ((time.year-start_date.year) + 1))#((time - start_date).days / 365))
                generator_data.loc[i, f'Benchmark Discounted Fuel Cost generator Total [$]'] += generator_data.loc[i, f'Benchmark Discounted Fuel Cost generator Unit {unit + 1} [$]']
            false_count_power_constraints = (generator_data[f"Power Constraints Unit {unit+1}"] == False).sum()
            logging.info(f'For Unit {unit+1} there are {false_count_power_constraints} (out of {len(generator_data)}) timestamps where the power was not in boundaries (minimum and maximum power)')
            if fuel_consumption_scope[unit] == "Total":
                benchmark_fuel_consumption = sum(generator_data[f'Benchmark Fuel Consumption generator Unit {unit + 1} [l]'])
                delta_fuel_consumption = model_fuel_consumption[unit] - benchmark_fuel_consumption
                delta_percentage = (delta_fuel_consumption/benchmark_fuel_consumption) * 100
                if delta_fuel_consumption > 0:
                    logging.info(f'The model fuel consumption is {delta_fuel_consumption}l higher than the benchmark fuel consumption')
                    logging.info(f'This is {delta_percentage} higher than the benchmark fuel consumption')
                if delta_fuel_consumption < 0:
                    logging.info(f'The model fuel consumption is {abs(delta_fuel_consumption)}l lower than the benchmark fuel consumption')
                    logging.info(f'This is {abs(delta_percentage)} % lower than the benchmark fuel consumption')
            else:
                generator_data.loc[i, f"Check Fuel Consumption Unit {unit+1}"] = (abs(((generator_data.loc[i, f'Model Fuel Consumption Unit {unit + 1} [l]']-generator_data.loc[i, f'Benchmark Fuel Consumption generator Unit {unit + 1} [l]'])/generator_data.loc[i, f'Benchmark Fuel Consumption generator Unit {unit + 1} [l]'])) < 0.01)
                false_count_fuel_consumption = (generator_data[f"Check Fuel Consumption Unit {unit+1}"] == False).sum()
                logging.info(f'For Unit {unit+1} the fuel consumption does not match the energy output for {false_count_fuel_consumption} (out of {len(generator_data)}) timestamps')
    else:
        for i in range(0, len(generator_data)):
            time = generator_data.loc[i, 'UTC Time']
            time = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            total_efficiency = sum(initial_efficiency[int(generator_type[unit].replace("Type ", "")) - 1] for unit in range(num_units)) / num_units
            if dynamic_efficiency:
                total_efficiency = sum(get_efficiency_from_tabular(generator_data.loc[i, f'Model generator Energy Unit {unit + 1} [Wh]'], int(generator_type[unit].replace("Type ", ""))) if dynamic_efficiency_type[int(generator_type[unit].replace("Type ", "")) - 1] == "Tabular Data" else get_efficiency_from_formula(generator_data.loc[i, f'Model generator Energy Unit {unit + 1} [Wh]'], int(generator_type[unit].replace("Type ", ""))) for unit in range(num_units)) / num_units
            if temporal_degradation:
                total_efficiency = sum(temporal_degradation_efficiency(total_efficiency, temporal_degradation_rate[int(generator_type[unit].replace("Type ", "")) - 1], time.date(), installation_dates[unit]) for unit in range(num_units)) / num_units
            generator_data.loc[i, 'Power Constraints Total'] = all(test_power_limits(generator_data.loc[i, f'Model generator Energy Unit {unit + 1} [Wh]'], max_powers[int(generator_type[unit].replace("Type ", "")) - 1], min_powers[int(generator_type[unit].replace("Type ", "")) - 1]) for unit in range(num_units))
            false_count_power_constraints = (generator_data['Power Constraints Total'] == False).sum()
            logging.info(f'There are {false_count_power_constraints} (out of {len(generator_data)}) timestamps where the power was not in boundaries (minimum and maximum power)')
            generator_data.loc[i, 'Benchmark Fuel Consumption generator Total [l]'] = get_fuel_consumption(total_power, lhv, total_efficiency)
        if fuel_consumption_scope[0] == "Total":
            benchmark_fuel_consumption = sum(generator_data['Benchmark Fuel Consumption generator Total [l]'])
            delta_fuel_consumption = model_fuel_consumption - benchmark_fuel_consumption
            delta_percentage = (delta_fuel_consumption/benchmark_fuel_consumption) * 100
            if delta_fuel_consumption > 0:
                logging.info(f'The model fuel consumption is {delta_fuel_consumption}l higher than the benchmark fuel consumption')
                logging.info(f'This is {delta_percentage} higher than the benchmark fuel consumption')
            if delta_fuel_consumption < 0:
                logging.info(f'The model fuel consumption is {abs(delta_fuel_consumption)}l lower than the benchmark fuel consumption')
                logging.info(f'This is {abs(delta_percentage)} lower than the benchmark fuel consumption')
        else:
            generator_data['Check Fuel Consumption Total'] = (abs(((generator_data['Model Fuel Consumption Total [l]']-generator_data['Benchmark Fuel Consumption generator Total [l]'])/generator_data['Benchmark Fuel Consumption generator Total [l]'])) < 0.01)
            false_count_fuel_consumption = (generator_data['Check Fuel Consumption Total'] == False).sum()
            logging.info(f'The fuel consumption does not match the energy output for {false_count_fuel_consumption} (out of {len(generator_data)}) timestamps')

    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "generator_validation.csv"
    generator_data.to_csv(results_data_path)