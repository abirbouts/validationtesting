import streamlit as st
import pandas as pd
import logging
from config.path_manager import PathManager
import datetime
import math
import numpy as np

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

def shear_exp(w_Z1: float, w_Z0: float, Z_1: float, Z_0: float, Z_rot: float, alpha: float) -> float:
    """
    Calculate the rotor wind speed using the shear exponent method.

    Parameters:
    w_Z1 (float): Wind speed at height Z_1.
    w_Z0 (float): Wind speed at height Z_0.
    Z_1 (float): Height Z_1.
    Z_0 (float): Height Z_0.
    Z_rot (float): Rotor height.

    Returns:
    float: Calculated rotor wind speed. If either w_Z1 or w_Z0 is zero, returns 0.
    """
    if alpha is None:
        if w_Z1 == 0 or w_Z0 == 0:
            alpha = 0
            U_rotor = 0
            return U_rotor
        else:
            alpha = (math.log(w_Z1) - math.log(w_Z0)) / (math.log(Z_1) - math.log(Z_0))
    U_rotor = w_Z1 * (Z_rot / Z_1) ** alpha
    return U_rotor

def get_wind_energy_two_heights(w_Z1: float, w_Z0: float, Z_1: float, Z_0: float, Z_rot: float, power_curve: pd.DataFrame, drivetrain_efficiency: float) -> float:
    U_rotor = shear_exp(w_Z1, w_Z0, Z_1, Z_0, Z_rot, alpha=None)
    wind_speeds_power_curve = power_curve['Wind Speed [m/s]'].values
    power_power_curve = power_curve['Power [W]'].values
    interpolated_value = np.interp(U_rotor, wind_speeds_power_curve, power_power_curve)
    wind_energy = interpolated_value * drivetrain_efficiency
    return wind_energy

def get_wind_energy_one_height(w_Z1: float, Z_1: float, Z_rot: float, power_curve: pd.DataFrame, drivetrain_efficiency: float, surface_roughness: float) -> float:
    alpha = 0.096 * math.log10(surface_roughness) + 0.16 * (math.log10(surface_roughness))**2 + 0.24
    U_rotor = shear_exp(w_Z1, None, Z_1, None, Z_rot, alpha)
    wind_speeds_power_curve = power_curve['Wind Speed [m/s]']
    power_power_curve = power_curve['Power [W]']
    interpolated_value = np.interp(U_rotor, wind_speeds_power_curve, power_power_curve)
    wind_energy = interpolated_value * drivetrain_efficiency
    return wind_energy

def wind_benchmark() -> None:
    logging.info('Running wind validation testing')
    project_name = st.session_state.get("project_name")
    wind_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"wind_data.csv"
    wind_data = pd.read_csv(wind_data_path)

    if wind_data['UTC Time'].str.match(r'^\d{2}-\d{2} \d{2}:\d{2}$').any():
        wind_data_columns = wind_data.columns.tolist()
        model_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_wind.csv"
        wind_model_data = pd.read_csv(model_data_path)
        wind_data.rename(columns={'UTC Time': 'UTC Time without year'}, inplace=True)
        wind_model_data['UTC Time without year'] = wind_model_data['UTC Time'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').strftime('%m-%d %H:%M'))
        wind_data['UTC Time without year'] = wind_data['UTC Time without year'].apply(lambda x: datetime.datetime.strptime(x, '%m-%d %H:%M').strftime('%m-%d %H:%M'))
        merged_data = pd.merge(wind_model_data, wind_data, on='UTC Time without year', how='left')
        wind_data = merged_data[wind_data_columns]

    num_units = st.session_state.wind_num_units
    installation_dates = st.session_state.wind_installation_dates_utc
    wind_type = st.session_state.wind_type
    initial_drivetrain_efficiency = [x / 100 for x in st.session_state.wind_drivetrain_efficiency]
    initial_inverter_efficiency = [x / 100 for x in st.session_state.wind_inverter_efficiency]
    lifetime = st.session_state.wind_lifetime
    hub_height = st.session_state.wind_hub_height
    temporal_degradation = st.session_state.battery_temporal_degradation
    temporal_degradation_rate = [x / 100 for x in st.session_state.wind_temporal_degradation_rate]
    complexity = st.session_state.wind_selected_input_type
    Z1 = st.session_state.wind_Z1
    Z0 = st.session_state.wind_Z0
    scope = st.session_state.wind_model_output_scope
    surface_roughness = st.session_state.wind_surface_roughness
    if scope == "Per Unit":
        for unit in range(num_units):
            wind_data[f'Benchmark wind Energy Unit {unit+1} [Wh]'] = 0
        wind_data['Benchmark wind Energy Total [Wh]'] = 0
    else:
        wind_data['Benchmark wind Energy Total [Wh]'] = 0

    for i in range(len(wind_data)):
        time = datetime.datetime.strptime(wind_data['UTC Time'][i], '%Y-%m-%d %H:%M:%S')
        for unit in range(num_units):
            type = wind_type[unit]
            type_int = int(type.replace("Type ", "")) - 1
            wind_power_curve_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"wind_power_curve_type_{type_int + 1}.csv"
            power_curve = pd.read_csv(wind_power_curve_path)
            if installation_dates[unit] > time or installation_dates[unit].replace(year=installation_dates[unit].year + lifetime[type_int]) < time:
                drivetrain_efficiency = 0
                inverter_efficiency = 0
            else:
                if temporal_degradation:
                    drivetrain_efficiency = temporal_degradation_efficiency(initial_drivetrain_efficiency[type_int], temporal_degradation_rate[type_int], time.date(), installation_dates[unit])
                    inverter_efficiency = temporal_degradation_efficiency(initial_inverter_efficiency[type_int], temporal_degradation_rate[type_int], time.date(), installation_dates[unit])
                else:
                    drivetrain_efficiency = initial_drivetrain_efficiency[type_int]
                    inverter_efficiency = initial_inverter_efficiency[type_int]

            if complexity == "Wind Speed given for one Height":
                w_Z1 = wind_data[f'Wind Speed {Z1}m [m/s]'][i]
                wind_energy = get_wind_energy_one_height(w_Z1, Z1, hub_height[type_int], power_curve, drivetrain_efficiency, surface_roughness)
                wind_energy = wind_energy * inverter_efficiency

            elif complexity == "Wind Speed given for two Heights":
                w_Z1 = wind_data[f'Wind Speed {Z1}m [m/s]'][i]
                w_Z0 = wind_data[f'Wind Speed {Z0}m [m/s]'][i]
                wind_energy = get_wind_energy_two_heights(w_Z1, w_Z0, Z1, Z0, hub_height[type_int], power_curve, drivetrain_efficiency)
                wind_energy = wind_energy * inverter_efficiency

            wind_data.at[i, f'Benchmark wind Energy Unit {unit+1} [Wh]'] = wind_energy
            wind_data.at[i, 'Benchmark wind Energy Total [Wh]'] += wind_energy

    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "wind_benchmark.csv"
    wind_data.to_csv(results_data_path)
    logging.info(f"Wind Benchmark saved in {results_data_path}")