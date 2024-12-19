import streamlit as st
import pandas as pd
from math import radians as rad, sin, cos, acos, degrees
import datetime
import logging
from config.path_manager import PathManager
import validationtesting.validation.get_solar_irradiance as get_solar_irradiance 


def get_solar_pv_energy(pv_calculation_type: str, nominal_power: float, PV_area: float, G_total: float, T_ambient: float, efficiency: float, dynamic_efficiency: bool, temperature_coefficient: float, T_ref: float, NOCT: float, T_ref_NOCT: float, ref_irradiance_NOCT: float, degradation: bool, degradation_rate: float, date: datetime.datetime, installation_date: datetime.datetime, lifetime: int) -> float:
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
    
    if pv_calculation_type == "Nominal Power":
        if degradation:
            years_installed = get_years_since_install(installation_date, date)
            nominal_power = nominal_power * (1 - (degradation_rate) * years_installed)

        if dynamic_efficiency:
            T_cell = T_ambient + ((NOCT - T_ref_NOCT) / ref_irradiance_NOCT) * G_total
            nominal_power = nominal_power * (1 + temperature_coefficient * (T_cell - T_ref))
        P_solar = (G_total/1000) * nominal_power

    elif pv_calculation_type == "Area and Efficiency":
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
    rho = st.session_state.get("pv_rho") / 100
    pv_calculation_type = st.session_state.get("solar_pv_calculation_type")
    nominal_power = st.session_state.get("pv_nominal_power")
    pv_area = st.session_state.get("pv_area")
    pv_efficiency = [x / 100 for x in st.session_state.pv_efficiency]
    pv_theta_tilt = st.session_state.get("pv_theta_tilt")
    pv_azimuth = st.session_state.get("pv_azimuth")
    pv_degradation = st.session_state.get("pv_degradation")
    pv_degradation_rate = [x / 100 for x in st.session_state.pv_degradation_rate]
    pv_temperature_dependent_efficiency = st.session_state.get("pv_temperature_dependent_efficiency")
    pv_temperature_coefficient = [x / 100 for x in st.session_state.pv_temperature_coefficient]
    pv_T_ref = st.session_state.get("pv_T_ref")
    pv_T_ref_NOCT = st.session_state.get("pv_T_ref_NOCT")
    pv_NOCT = st.session_state.get("pv_NOCT")
    pv_I_ref_NOCT = st.session_state.get("pv_I_ref_NOCT")
    pv_dynamic_inverter_efficiency = st.session_state.get("pv_dynamic_inverter_efficiency")
    pv_inverter_efficiency = [x / 100 for x in st.session_state.pv_inverter_efficiency]
    discount_rate = st.session_state.get("discount_rate") / 100
    start_date = st.session_state.get("start_date")

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
        if st.session_state['solar_pv_curtailment']:
            for unit in range(num_units):
                irradiation_data_columns.append(f'Model solar_pv Used Energy Unit {unit + 1} [Wh]')
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
            date = irradiation_data.loc[i, 'UTC Time']
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            time = date.time()
            time_float = time.hour + time.minute / 60
            day_of_year = date.timetuple().tm_yday
            for type in solar_pv_types:
                type_int = int(type.replace("Type ", ""))
                if Input_GHI and Input_DHI:
                    irradiation_data.loc[i, f'Benchmark G Total {type} [W/m^2]'] = get_solar_irradiance.with_GHI_DHI(pv_theta_tilt[type_int -1], irradiation_data.loc[i, 'GHI [W/m^2]'], irradiation_data.loc[i, 'DHI [W/m^2]'], rho, lat, lon, day_of_year, time_float, pv_azimuth[type_int -1])
                if Input_DHI and Input_DNI:
                    irradiation_data.loc[i, f'Benchmark G Total {type} [W/m^2]'] = get_solar_irradiance.with_DNI_DHI(pv_theta_tilt[type_int -1], irradiation_data.loc[i, 'DNI [W/m^2]'], irradiation_data[i, 'DHI [W/m^2]'], 0.2, lat, lon, days_in_year, day_of_year, time_float, True)
    
    for unit in range(num_units):
        irradiation_data[f"Benchmark solar_pv Energy Unit {unit+1} [Wh]"] = None
        irradiation_data[f'Benchmark solar_pv Discounted Energy Unit {unit+1} [Wh]'] = None
        irradiation_data[f'Benchmark Curtailed solar_pv Energy Unit {unit + 1} [Wh]'] = None
        if st.session_state[f'solar_pv_curtailment'][unit]:
            irradiation_data[f'Benchmark solar_pv Discounted Used Energy Unit {unit+1} [Wh]'] = 0

    irradiation_data[f'Benchmark solar_pv Energy Total [Wh]'] = 0
    irradiation_data[f'Benchmark solar_pv Discounted Energy Total [Wh]'] = 0
    irradiation_data[f'Benchmark Curtailed solar_pv Energy Total [Wh]'] = 0
    if st.session_state['solar_pv_curtailment']:
        irradiation_data[f'Benchmark solar_pv Discounted Used Energy Total [Wh]'] = 0
    
    previous_results = {}
    for i in range(0, len(irradiation_data)):
        for unit in range(num_units):
            type = solar_pv_type[unit]
            key = (installation_dates[unit], type, i)
            if key in previous_results:
                irradiation_data.loc[i, f'Benchmark solar_pv Energy Unit {unit+1} [Wh]'] = previous_results[key]
            else:
                type_int = int(type.replace("Type ", ""))
                date = irradiation_data.loc[i, 'UTC Time']
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                if pv_temperature_dependent_efficiency:
                    Temperature = irradiation_data.loc[i, f'Temperature [°C]']
                else:
                    Temperature = None
                energy = get_solar_pv_energy(pv_calculation_type[type_int-1], nominal_power[type_int-1], pv_area[type_int-1], irradiation_data.loc[i, f'Benchmark G Total {type} [W/m^2]'], Temperature, pv_efficiency[type_int-1], pv_temperature_dependent_efficiency, pv_temperature_coefficient[type_int-1], pv_T_ref[type_int-1], pv_NOCT[type_int-1], pv_T_ref_NOCT[type_int-1], pv_I_ref_NOCT[type_int-1], pv_degradation, pv_degradation_rate[type_int-1], date, installation_dates[unit], pv_lifetime[type_int-1])
                if pv_dynamic_inverter_efficiency:
                    pass
                else:
                    energy = energy * pv_inverter_efficiency[type_int-1]
                irradiation_data.loc[i, f'Benchmark solar_pv Energy Unit {unit+1} [Wh]'] = energy
                if st.session_state[f'solar_pv_curtailment'][unit]:
                    irradiation_data.loc[i, f'Benchmark Curtailed solar_pv Energy Unit {unit + 1} [Wh]'] = max(0, energy - irradiation_data.loc[i, f'Model solar_pv Used Energy Unit {unit + 1} [Wh]'])
                    irradiation_data.loc[i, f'Benchmark solar_pv Discounted Used Energy Unit {unit+1} [Wh]'] = min(energy, irradiation_data.loc[i, f'Model solar_pv Used Energy Unit {unit + 1} [Wh]']) / ((1 + discount_rate) ** ((date - start_date).days / 365))
                irradiation_data.loc[i, f'Benchmark solar_pv Discounted Energy Unit {unit+1} [Wh]'] = energy / ((1 + discount_rate) ** ((date - start_date).days / 365))
                previous_results[key] = energy
            irradiation_data.loc[i, f'Benchmark solar_pv Energy Total [Wh]'] += irradiation_data.loc[i, f'Benchmark solar_pv Energy Unit {unit+1} [Wh]']
            irradiation_data.loc[i, f'Benchmark solar_pv Discounted Energy Total [Wh]'] += irradiation_data.loc[i, f'Benchmark solar_pv Discounted Energy Unit {unit+1} [Wh]']
            if st.session_state[f'solar_pv_curtailment'][unit]:
                irradiation_data.loc[i, f'Benchmark Curtailed solar_pv Energy Total [Wh]'] += irradiation_data.loc[i, f'Benchmark Curtailed solar_pv Energy Unit {unit + 1} [Wh]']
                irradiation_data.loc[i, f'Benchmark solar_pv Discounted Used Energy Total [Wh]'] += irradiation_data.loc[i, f'Benchmark solar_pv Discounted Used Energy Unit {unit+1} [Wh]']
    for unit in range(num_units):
        if st.session_state[f'solar_pv_curtailment'][unit]:
            irradiation_data.drop(columns=[f'Model solar_pv Used Energy Unit {unit + 1} [Wh]'], inplace=True)


    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "solar_pv_validation.csv"
    irradiation_data.to_csv(results_data_path)
    logging.info(f"Solar PV Benchmark saved in {results_data_path}")