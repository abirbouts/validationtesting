"""
This module is used to calculate the benchmark wind energy output of a wind turbine. 
It uses the wind speed data and the power curve of the wind turbine to calculate the energy output. 
The energy output is calculated for each unit of the wind turbine and for each time step in the wind speed data. 
The energy output is then saved to a CSV file.
"""

import streamlit as st
import pandas as pd
import logging
from config.path_manager import PathManager
import datetime
import math
import numpy as np

def temporal_degradation_efficiency(efficiency: float, degradation_rate: float, date: datetime.date, installation_date: datetime.date) -> float:
    """
    Calculate the efficiency of a component based on the degradation rate and the time since installation.
    """
    def get_years_since_install(installation_date: datetime.date, current_date: datetime.date) -> float:
        # Ensure both are date objects
        installation_date = installation_date.date()
        days_since_install = (current_date - installation_date).days
        years_since_install = days_since_install / 365.25
        return years_since_install

    years_installed = get_years_since_install(installation_date, date)
    efficiency = efficiency * (1 - degradation_rate * years_installed)
    return efficiency

def shear_exp(w_Z1: float, w_Z0: float, Z_1: float, Z_0: float, Z_rot: float, alpha: float) -> float:
    """
    Calculate the rotor wind speed using the shear exponent method.
    """
    if alpha is None:
        if w_Z1 == 0 or w_Z0 == 0:
            return 0
        else:
            alpha = (math.log(w_Z1) - math.log(w_Z0)) / (math.log(Z_1) - math.log(Z_0))
    U_rotor = w_Z1 * (Z_rot / Z_1) ** alpha
    return U_rotor

def get_wind_energy_two_heights(w_Z1: float, w_Z0: float, Z_1: float, Z_0: float, Z_rot: float, power_curve: pd.DataFrame, drivetrain_efficiency: float) -> float:
    """
    Get the wind energy output using wind speeds at two heights.
    """
    U_rotor = shear_exp(w_Z1, w_Z0, Z_1, Z_0, Z_rot, alpha=None)
    wind_speeds = power_curve['Wind Speed [m/s]'].values
    power_values = power_curve['Power [W]'].values
    interpolated_power = np.interp(U_rotor, wind_speeds, power_values)
    wind_energy = interpolated_power * drivetrain_efficiency
    return wind_energy

def get_wind_energy_one_height(w_Z1: float, Z_1: float, Z_rot: float, power_curve: pd.DataFrame, drivetrain_efficiency: float, surface_roughness: float) -> float:
    """
    Get the wind energy output using wind speed measured at one height.
    """
    # Compute an empirical shear exponent based on surface roughness.
    alpha = 0.096 * math.log10(surface_roughness) + 0.16 * (math.log10(surface_roughness))**2 + 0.24
    U_rotor = shear_exp(w_Z1, None, Z_1, None, Z_rot, alpha)
    wind_speeds = power_curve['Wind Speed [m/s]']
    power_values = power_curve['Power [W]']
    interpolated_power = np.interp(U_rotor, wind_speeds, power_values)
    wind_energy = interpolated_power * drivetrain_efficiency
    return wind_energy

def calculate_yearly_wind_energy(wind_data: pd.DataFrame, unique_wind_types: list, complexity: str, 
                                 Z1: float, Z0: float, hub_heights: list, 
                                 initial_drivetrain_efficiencies: list, 
                                 surface_roughness: float, project_name: str) -> dict:
    """
    Precompute hourly wind energy for a representative year for each unique wind turbine type.
    Returns a dictionary where each key is a turbine type (e.g., "Type 1")
    and its value is a list (length 365) of daily energy profiles (each a pandas Series).
    """
    wind_data = wind_data[~((wind_data['Time'].dt.month == 2) & (wind_data['Time'].dt.day == 29))]
    wind_data['Day of Year'] = wind_data['Time'].dt.dayofyear
    wind_data['Hour'] = wind_data['Time'].dt.hour
    yearly_wind_energy = {}
    for wind_type in unique_wind_types:
        type_int = int(wind_type.replace("Type ", "")) - 1
        hub = hub_heights[type_int]
        drivetrain_eff = initial_drivetrain_efficiencies[type_int]
        # Load the corresponding power curve file.
        wind_power_curve_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"wind_power_curve_type_{type_int + 1}.csv"
        power_curve = pd.read_csv(wind_power_curve_path)
        # Group the wind data by day.
        daily_groups = wind_data.groupby('Day of Year')
        daily_profiles = []
        # Loop over days 1 to 365.
        for day in range(1, 366):
            if day in daily_groups.groups:
                daily_data = daily_groups.get_group(day).sort_values('Hour')
                hourly_energy = []
                for _, row in daily_data.iterrows():
                    if complexity == "Wind Speed given for one Height":
                        w_Z1 = row[f'Wind Speed {Z1}m [m/s]']
                        energy = get_wind_energy_one_height(w_Z1, Z1, hub, power_curve, drivetrain_eff, surface_roughness)
                    elif complexity == "Wind Speed given for two Heights":
                        w_Z1 = row[f'Wind Speed {Z1}m [m/s]']
                        w_Z0 = row[f'Wind Speed {Z0}m [m/s]']
                        energy = get_wind_energy_two_heights(w_Z1, w_Z0, Z1, Z0, hub, power_curve, drivetrain_eff)
                    else:
                        energy = 0
                    hourly_energy.append(energy)
                daily_series = pd.Series(hourly_energy)
            else:
                # If there is no data for this day, fill with zeros (assume 24 hours).
                daily_series = pd.Series([0] * 24)
            daily_profiles.append(daily_series)
        yearly_wind_energy[wind_type] = daily_profiles
    return yearly_wind_energy

def fill_wind_table(start_date: datetime.datetime, end_date: datetime.datetime, 
                    installation_dates: list, wind_lifetime: list, yearly_wind_energy: dict, 
                    wind_unit_types: list, wind_degradation: bool, wind_degradation_rate: list, 
                    discount_rate: float) -> pd.DataFrame:
    """
    Fill out an hourly table for the project timeline using the precomputed yearly wind energy profiles.
    For each turbine unit, if the current timestamp is outside its operational period 
    (before installation or after end-of-life), energy is set to zero. Otherwise the base energy
    is modified by degradation.
    """
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    date_range = date_range[~((date_range.month == 2) & (date_range.day == 29))]
    results = pd.DataFrame(index=date_range)

    num_units = len(wind_unit_types)
    for unit in range(num_units):
        results[f'Benchmark wind Energy Unit {unit+1} [Wh]'] = 0
    results['Benchmark wind Energy Total [Wh]'] = 0

    # Create a dictionary to store previously calculated results
    calculated_units = {}

    # Loop over each turbine unit.
    for unit in range(num_units):
        turbine_type = wind_unit_types[unit]
        install_date = installation_dates[unit]
        key = (turbine_type, install_date)  # Key for duplicate detection

        # Determine type index to obtain lifetime and degradation rate.
        type_int = int(turbine_type.replace("Type ", "")) - 1
        lifetime_years = wind_lifetime[type_int]
        end_of_life = install_date + datetime.timedelta(days=lifetime_years * 365)
        # Get the precomputed yearly energy profile for this turbine type.
        base_yearly_energy = yearly_wind_energy[turbine_type]
        col_name = f'Benchmark wind Energy Unit {unit+1} [Wh]'

        # Check if a unit with the same turbine type and installation date was already calculated.
        if key in calculated_units:
            # Copy the precomputed series into this unit’s column.
            results[col_name] = calculated_units[key]
            results['Benchmark wind Energy Total [Wh]'] += calculated_units[key]
        else:
            # Compute new energy series for this unit.
            new_unit_series = pd.Series(0, index=date_range)
            for current_time in date_range:
                if current_time < install_date or current_time > end_of_life:
                    energy = 0
                else:
                    # Adjust day index, account for leap years.
                    if current_time.is_leap_year and current_time.month > 2:
                        day_index = current_time.dayofyear - 2
                    else:
                        day_index = current_time.dayofyear - 1
                    hour_index = current_time.hour
                    # Retrieve the base energy from the daily profile.
                    if 0 <= day_index < len(base_yearly_energy):
                        daily_series = base_yearly_energy[day_index]
                        if hour_index < len(daily_series):
                            base_energy = daily_series.iloc[hour_index]
                        else:
                            base_energy = 0
                    else:
                        base_energy = 0
                    energy = base_energy
                    # Apply temporal degradation if enabled.
                    if wind_degradation:
                        years_since_install = (current_time - install_date).days // 365
                        energy *= (1 - wind_degradation_rate[type_int] * years_since_install)
                new_unit_series.at[current_time] = energy
                # Add energy to the total column.
                results.at[current_time, 'Benchmark wind Energy Total [Wh]'] += energy

            results[col_name] = new_unit_series
            calculated_units[key] = new_unit_series

    results.reset_index(inplace=True)
    results.rename(columns={'index': 'Time'}, inplace=True)
    return results

def wind_benchmark() -> None:
    """
    Wind Benchmark Calculation.
    This function loads the wind data, precomputes a yearly wind energy profile for each turbine type,
    fills in an hourly table over the project timeline (applying installation, lifetime, degradation and discounting),
    and saves the results to a CSV file.
    """
    project_name = st.session_state.get("project_name")
    wind_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / "wind_data.csv"
    wind_data = pd.read_csv(wind_data_path)


    # Add dummy year 2001, a non-leap year
    wind_data['Time'] = '2001-' + wind_data['Time'].astype(str) 
    wind_data['Time'] = pd.to_datetime(wind_data['Time'], format='%Y-%m-%d %H:%M', errors='coerce')

    # Retrieve parameters from session_state
    wind_num_units = st.session_state.wind_num_units
    installation_dates = st.session_state.wind_installation_dates
    wind_unit_types = st.session_state.wind_type  
    initial_drivetrain_efficiencies = [x / 100 for x in st.session_state.wind_drivetrain_efficiency]
    wind_lifetime = st.session_state.wind_lifetime
    hub_heights = st.session_state.wind_hub_height
    wind_degradation = st.session_state.battery_temporal_degradation
    wind_degradation_rate = [x / 100 for x in st.session_state.wind_temporal_degradation_rate]
    complexity = st.session_state.wind_selected_input_type
    Z1 = st.session_state.wind_Z1
    Z0 = st.session_state.wind_Z0
    surface_roughness = st.session_state.wind_surface_roughness
    discount_rate = st.session_state.get("discount_rate") / 100
    start_date = st.session_state.get("start_date")
    end_date = st.session_state.get("end_date")

    st.write("--------------------")
    progress_step = 1/3
    wind_progress = 0
    wind_progress_bar = st.progress(wind_progress)
    wind_text = st.empty()

    # Precompute the yearly wind energy profiles for each turbine type
    wind_text.write("Computing Yearly Wind Energy Profiles for Reference Year")
    unique_wind_types = list(set(wind_unit_types))
    yearly_wind_energy = calculate_yearly_wind_energy(
        wind_data, unique_wind_types, complexity, Z1, Z0, hub_heights,
        initial_drivetrain_efficiencies, surface_roughness, project_name
    )
    wind_progress += progress_step
    wind_progress_bar.progress(wind_progress)

    # Fill the hourly wind energy table for the full project timeline
    wind_text.write("Calculating Wind Energy for the Project Timeline")
    results = fill_wind_table(
        start_date, end_date, installation_dates, wind_lifetime, yearly_wind_energy, wind_unit_types,
        wind_degradation, wind_degradation_rate, discount_rate
    )
    wind_progress += progress_step
    wind_progress_bar.progress(wind_progress)

    # Save the results
    wind_text.write("Saving Wind Benchmark Results")
    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "wind_validation.csv"
    results.to_csv(results_data_path, index=False)
    wind_text.write("Wind Benchmark Optimization Completed")
    wind_progress += progress_step
    wind_progress_bar.progress(wind_progress)