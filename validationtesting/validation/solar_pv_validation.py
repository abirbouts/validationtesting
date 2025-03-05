"""
This module is used to calculate the benchmark solar PV energy output of a solar PV system.
It uses the solar irradiance data and the specifications of the solar PV system to calculate the energy output.
The energy output is calculated for each unit of the solar PV system and for each time step in the solar irradiance data.
The energy output is then saved to a CSV file.
"""

import streamlit as st
import pandas as pd
import datetime
from config.path_manager import PathManager
import validationtesting.validation.get_solar_irradiance as get_solar_irradiance

def calculate_g_total(irradiation_data, solar_pv_types, pv_theta_tilt, pv_azimuth, lat, lon, rho, timezone):
    """
    Calculate G Total for each type and add it to the irradiation data.
    """
    for type_index, pv_type in enumerate(solar_pv_types):
        g_total_column = f"Benchmark G Total {pv_type} [W/m^2]"
        irradiation_data[g_total_column] = None

        for i, row in irradiation_data.iterrows():
            day_of_year = datetime.datetime.strptime(row['Time'], '%m-%d %H:%M').timetuple().tm_yday
            date_time = datetime.datetime.strptime(row['Time'], '%m-%d %H:%M')

            G_total = get_solar_irradiance.with_GHI_DHI(
                pv_theta_tilt[type_index], row['GHI [W/m^2]'], row['DHI [W/m^2]'], rho, lat, lon, day_of_year, date_time, timezone, pv_azimuth[type_index]
            )

            irradiation_data.at[i, g_total_column] = G_total

    return irradiation_data


def calculate_yearly_pv_energy(solar_pv_types, pv_calculation_type, nominal_power, pv_area, pv_efficiency, pv_theta_tilt, pv_azimuth, pv_temperature_dependent_efficiency, pv_temperature_coefficient, pv_T_ref, pv_NOCT, pv_T_ref_NOCT, pv_I_ref_NOCT, lat, lon, rho, yearly_irradiation):
    """
    Precompute solar PV energy for one year for each type.
    """
    yearly_pv_energy = {}

    for type_index, pv_type in enumerate(solar_pv_types):
        type_energy = []
        for day_of_year, daily_data in yearly_irradiation.items():
            G_total = daily_data[f"Benchmark G Total {pv_type} [W/m^2]"]
            if pv_temperature_dependent_efficiency:
                T_ambient = daily_data.get("Temperature [°C]", None)

            if pv_calculation_type[type_index] == "Nominal Power":
                if pv_temperature_dependent_efficiency:
                    T_cell = (T_ambient + ((pv_NOCT[type_index] - pv_T_ref_NOCT[type_index]) / pv_I_ref_NOCT[type_index]) * G_total)
                    power = nominal_power[type_index] * (1 + (pv_temperature_coefficient[type_index] * (T_cell - pv_T_ref[type_index])))
                else:
                    power = nominal_power[type_index]
                energy = (G_total / 1000) * power
            elif pv_calculation_type[type_index] == "Area and Efficiency":
                if pv_temperature_dependent_efficiency:
                    efficiency = pv_efficiency[type_index] * (1 + (pv_temperature_coefficient[type_index] * (T_cell - pv_T_ref[type_index])))
                else:
                    efficiency = pv_efficiency[type_index]
                energy = pv_area[type_index] * G_total * efficiency

            type_energy.append(energy)

        yearly_pv_energy[pv_type] = type_energy
    return yearly_pv_energy


def fill_pv_table(start_date, end_date, installation_dates, pv_lifetime, yearly_pv_energy, solar_pv_types, pv_degradation, pv_degradation_rate, pv_units):
    """
    Fill out the table based on the installation date, lifetime, and degradation hour by hour.
    """
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    date_range = date_range[~((date_range.month == 2) & (date_range.day == 29))]
    column_names = [f"Benchmark solar_pv Energy Unit {unit + 1} [Wh]" for unit in range(pv_units)]
    column_names.append("Benchmark solar_pv Energy Total [Wh]")
    results = pd.DataFrame(index=date_range, columns=column_names)
    results["Benchmark solar_pv Energy Total [Wh]"] = 0
    for unit, (install_date, lifetime, pv_type) in enumerate(zip(installation_dates, pv_lifetime, solar_pv_types)):
        end_of_life = install_date + datetime.timedelta(days=lifetime * 365)
        yearly_energy = yearly_pv_energy[pv_type]
        for date in date_range:
            if date < install_date or date > end_of_life:
                energy = 0
            else:
                if date.is_leap_year and date.month > 2:
                    day_index = date.dayofyear - 2 
                else:
                    day_index = date.dayofyear - 1
                hour_index = date.hour
                energy = yearly_energy[day_index].iloc[hour_index]
                if pv_degradation:
                    years_since_install = (date - install_date).days // 365
                    energy *= (1 - (pv_degradation_rate / 100) * years_since_install)
            results.at[date, f"Benchmark solar_pv Energy Unit {unit + 1} [Wh]"] = energy
            results.at[date, "Benchmark solar_pv Energy Total [Wh]"] += energy
    results.reset_index(inplace=True)
    results.rename(columns={'index': 'Time'}, inplace=True)
    return results


def solar_pv_benchmark():
    """
    Solar PV Benchmark Calculation.
    """
    # Load necessary data
    timezone = st.session_state.get("timezone")
    solar_pv_types = st.session_state.get("solar_pv_types")
    start_date = st.session_state.get("start_date")
    end_date = st.session_state.get("end_date")
    installation_dates = st.session_state.get("installation_dates")
    pv_lifetime = st.session_state.get("pv_lifetime")
    pv_units = st.session_state.get("solar_pv_num_units")
    nominal_power = st.session_state.get("pv_nominal_power")
    pv_area = st.session_state.get("pv_area")
    pv_efficiency = [x / 100 for x in st.session_state.pv_efficiency]
    pv_temperature_dependent_efficiency = st.session_state.get("pv_temperature_dependent_efficiency")
    pv_temperature_coefficient = [x / 100 for x in st.session_state.pv_temperature_coefficient]
    pv_T_ref = st.session_state.get("pv_T_ref")
    pv_NOCT = st.session_state.get("pv_NOCT")
    pv_T_ref_NOCT = st.session_state.get("pv_T_ref_NOCT")
    pv_I_ref_NOCT = st.session_state.get("pv_I_ref_NOCT")
    pv_degradation = st.session_state.get("pv_degradation")
    pv_degradation_rate = [x / 100 for x in st.session_state.pv_degradation_rate]

    lat = st.session_state.get("lat")
    lon = st.session_state.get("lon")
    rho = st.session_state.get("pv_rho") / 100

    st.write("--------------------")
    progress_step = 0.20
    solar_pv_progress = 0
    solar_pv_progress_bar = st.progress(solar_pv_progress)
    solar_pv_text = st.empty()

    # Load Solar Irradiation Data
    solar_pv_text.write("Loading Solar Irradiation Data")
    irradiation_data = pd.read_csv(PathManager.PROJECTS_FOLDER_PATH / str(st.session_state.get("project_name")) / "inputs" / "solar_irradiation.csv")
    solar_pv_progress += progress_step
    solar_pv_progress_bar.progress(solar_pv_progress)

    # Extract Day of Year from Time
    solar_pv_text.write("Calculating Irradiation on Tilted Surface for Reference Year")
    irradiation_data['Day of Year'] = irradiation_data['Time'].apply(lambda x: datetime.datetime.strptime(x, '%m-%d %H:%M').timetuple().tm_yday)
    irradiation_data = calculate_g_total(irradiation_data, solar_pv_types, st.session_state.get("pv_theta_tilt"), st.session_state.get("pv_azimuth"), lat, lon, rho, timezone)
    yearly_irradiation = {day: group for day, group in irradiation_data.groupby('Day of Year')}
    solar_pv_progress += progress_step
    solar_pv_progress_bar.progress(solar_pv_progress)

    # PV energy for reference year
    solar_pv_text.write("Calculating Yearly PV Energy for Reference Year")
    yearly_pv_energy = calculate_yearly_pv_energy(
        solar_pv_types, st.session_state.get("solar_pv_calculation_type"), nominal_power, pv_area, pv_efficiency,
        st.session_state.get("pv_theta_tilt"), st.session_state.get("pv_azimuth"),
        pv_temperature_dependent_efficiency, pv_temperature_coefficient, pv_T_ref, pv_NOCT, pv_T_ref_NOCT,
        pv_I_ref_NOCT, lat, lon, rho, yearly_irradiation
    )
    solar_pv_progress += progress_step
    solar_pv_progress_bar.progress(solar_pv_progress)

    # Fill the PV energy table for the entire project timeline
    solar_pv_text.write("Calculating Solar PV Energy for the Project Timeline")
    results = fill_pv_table(
        start_date, end_date, installation_dates, pv_lifetime, yearly_pv_energy, solar_pv_types,
        pv_degradation, pv_degradation_rate, pv_units
    )
    solar_pv_progress += progress_step
    solar_pv_progress_bar.progress(solar_pv_progress)


    # Save the results
    solar_pv_text.write("Saving Solar PV Benchmark Results")
    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(st.session_state.get("project_name")) / "results" / "solar_pv_validation.csv"
    results.to_csv(results_data_path)
    solar_pv_text.write("Solar PV Benchmark Calculation Completed.")
    solar_pv_progress += progress_step
    solar_pv_progress_bar.progress(solar_pv_progress)