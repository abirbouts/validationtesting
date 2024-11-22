import streamlit as st
import pandas as pd
from math import radians as rad, sin, cos, acos, degrees
import datetime
import logging
from config.path_manager import PathManager
import validationtesting.validation.get_solar_irradiance as get_solar_irradiance 


def get_solar_pv_power(PV_area: float, G_total: float, T_ambient: float, efficiency: float, dynamic_efficiency: bool, temperature_coefficient: float, T_ref: float, NOCT: float, T_ref_NOCT: float, ref_irradiance_NOCT: float, degradation: bool, degradation_rate: float, date: datetime.datetime, installation_date: datetime.datetime, lifetime: int) -> float:
    def get_years_since_install(installation_date: datetime.date, current_date: datetime.date) -> float:
        # Ensure both are 'date' objects
        installation_date = installation_date.date()
        current_date = current_date.date()
        
        # Calculate the difference in days and convert to years
        days_since_install = (current_date - installation_date).days
        years_since_install = days_since_install / 365.25
        return years_since_install

    if date < installation_date:
        return 0
    
    end_of_life = installation_date.replace(year=installation_date.year + lifetime)

    try:
        end_of_life = installation_date.replace(year=installation_date.year + lifetime)
    except ValueError:
        end_of_life = installation_date.replace(year=installation_date.year + lifetime, day=28)

    if date > end_of_life:
        return 0
    
    if degradation:
        years_installed = get_years_since_install(installation_date, date)
        efficiency = efficiency * (1 - (degradation_rate / 100) * years_installed)

    if dynamic_efficiency:
        T_cell = T_ambient + ((NOCT - T_ref_NOCT) / ref_irradiance_NOCT) * G_total
        efficiency = efficiency * (1 + temperature_coefficient * (T_cell - T_ref))
    
    P_solar = PV_area * G_total * efficiency
    return P_solar

def add_inverter_efficiency(P_solar: float, inverter_efficiency: dict) -> tuple:
    for start, end, efficiency in zip(inverter_efficiency["Power_Start_W"], 
                                    inverter_efficiency["Power_End_W"], 
                                    inverter_efficiency["Inverter_Efficiency_%"]):
        if start <= P_solar < end:
            inverter_efficiency = efficiency
    P_solar_final = inverter_efficiency * P_solar
    return P_solar_final, inverter_efficiency
    

def solar_pv_benchmark() -> None:
    logging.info('Running Solar PV benchmarking')
    num_units = st.session_state.get("solar_pv_num_units")
    installation_dates = st.session_state.get("installation_dates")
    num_solar_pv_types = st.session_state.get("num_solar_pv_types")
    solar_pv_types = st.session_state.get("solar_pv_types")
    solar_pv_type = st.session_state.get("solar_pv_type")
    pv_lifetime = st.session_state.get("pv_lifetime") 
    pv_area = st.session_state.get("pv_area")
    pv_efficiency = [x / 100 for x in st.session_state.pv_efficiency]
    pv_theta_tilt = st.session_state.get("pv_theta_tilt")
    pv_degradation = st.session_state.get("pv_degradation")
    pv_degradation_rate = st.session_state.get("pv_degradation_rate")
    pv_temperature_dependent_efficiency = st.session_state.get("pv_temperature_dependent_efficiency")
    pv_temperature_coefficient = st.session_state.get("pv_temperature_coefficient")
    pv_T_ref = st.session_state.get("pv_T_ref")
    pv_T_ref_NOCT = st.session_state.get("pv_T_ref_NOCT")
    pv_NOCT = st.session_state.get("pv_NOCT")
    pv_I_ref_NOCT = st.session_state.get("pv_I_ref_NOCT")
    pv_dynamic_inverter_efficiency = st.session_state.get("pv_dynamic_inverter_efficiency")
    pv_inverter_efficiency = [x / 100 for x in st.session_state.pv_inverter_efficiency]

    lon = st.session_state.get("lon")
    lat = st.session_state.get("lat")

    Input_G_total = st.session_state.get("Input_G_total")
    Input_GHI = st.session_state.get("Input_GHI")
    Input_DHI = st.session_state.get("Input_DHI")
    Input_DNI = st.session_state.get("Input_DNI")

    project_name = st.session_state.get("project_name")
    irradiation_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / "solar_irradiation.csv"
    irradiation_data = pd.read_csv(irradiation_data_path)
    
    if irradiation_data['UTC Time'].str.match(r'^\d{2}-\d{2} \d{2}:\d{2}$').any():
        irradiation_data_columns = irradiation_data.columns.tolist()
        model_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_solar_pv.csv"
        solar_model_data = pd.read_csv(model_data_path)
        irradiation_data.rename(columns={'UTC Time': 'UTC Time without year'}, inplace=True)
        solar_model_data['UTC Time without year'] = solar_model_data['UTC Time'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').strftime('%m-%d %H:%M'))
        irradiation_data['UTC Time without year'] = irradiation_data['UTC Time without year'].apply(lambda x: datetime.datetime.strptime(x, '%m-%d %H:%M').strftime('%m-%d %H:%M'))
        merged_data = pd.merge(solar_model_data, irradiation_data, on='UTC Time without year', how='left')
        irradiation_data = merged_data[irradiation_data_columns]

    if st.session_state.Input_G_total:
        for type in solar_pv_types:
            irradiation_data[f"Benchmark G Total {type} [W/m^2]"] = irradiation_data["G Total [W/m^2]"]

    else:
        for type in solar_pv_types:
            irradiation_data[f"Benchmark G Total {type} [W/m^2]"] = None
        
        for i in range(0, len(irradiation_data)):
            date = irradiation_data['UTC Time'][i]
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            time = date.time()
            time_float = time.hour + time.minute / 60
            day_of_year = date.timetuple().tm_yday
            is_leap_year = (date.year % 4 == 0 and date.year % 100 != 0) or (date.year % 400 == 0)
            days_in_year = 366 if is_leap_year else 365
            for type in solar_pv_types:
                type_int = int(type.replace("Type ", ""))
                if Input_GHI and Input_DHI:
                    irradiation_data[f'Benchmark G Total {type} [W/m^2]'][i] = get_solar_irradiance.with_GHI_DHI(pv_theta_tilt[type_int -1], irradiation_data['GHI [W/m^2]'][i], irradiation_data['DHI [W/m^2]'][i], 0.2, lat, lon, days_in_year, day_of_year, time_float, True)
                if Input_DHI and Input_DNI:
                    irradiation_data[f'Benchmark G Total {type} [W/m^2]'][i] = get_solar_irradiance.with_DNI_DHI(pv_theta_tilt[type_int -1], irradiation_data['DNI [W/m^2]'][i], irradiation_data['DHI [W/m^2]'][i], 0.2, lat, lon, days_in_year, day_of_year, time_float, True)
    
    for unit in range(num_units):
        irradiation_data[f"Benchmark solar_pv Power Unit {unit+1} [W]"] = None
        
    irradiation_data[f'Benchmark solar_pv Power Total [W]'] = 0
    
    for i in range(0, len(irradiation_data)):
        for unit in range(num_units):
            date = irradiation_data['UTC Time'][i]
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            type = solar_pv_type[unit]
            type_int = int(type.replace("Type ", ""))
            if pv_temperature_dependent_efficiency:
                Temperature = irradiation_data[f'Temperature'][i]
            else:
                Temperature = None
            irradiation_data[f'Benchmark solar_pv Power Unit {unit+1} [W]'][i] = get_solar_pv_power(pv_area[type_int-1], irradiation_data[f'Benchmark G Total {type} [W/m^2]'][i], Temperature, pv_efficiency[type_int-1], pv_temperature_dependent_efficiency, pv_temperature_coefficient[type_int-1], pv_T_ref[type_int-1], pv_NOCT[type_int-1], pv_T_ref_NOCT[type_int-1], pv_I_ref_NOCT[type_int-1], pv_degradation, pv_degradation_rate[type_int-1], date, installation_dates[unit], pv_lifetime[type_int-1])
            irradiation_data[f'Benchmark solar_pv Power Total [W]'][i] += irradiation_data[f'Benchmark solar_pv Power Unit {unit+1} [W]'][i]
    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "solar_pv_benchmark.csv"
    irradiation_data.to_csv(results_data_path)
    st.write(irradiation_data)
    logging.info(f"Solar PV Benchmark saved in {results_data_path}")