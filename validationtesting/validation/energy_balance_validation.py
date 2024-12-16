import streamlit as st
import pandas as pd
from config.path_manager import PathManager


def energy_balance_validation() -> None:
    project_name = st.session_state.get("project_name")    

    used_components = []
    used_components.append("consumption")
    if st.session_state.solar_pv:
        used_components.append("solar_pv")
    if st.session_state.wind:
        used_components.append("wind")
    if st.session_state.generator:
        used_components.append("generator")
    if st.session_state.battery:
        used_components.append("battery")

    combined_energy = pd.DataFrame()
    for component in used_components:
        project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_{component}.csv"
        df = pd.read_csv(project_folder_path)
        if combined_energy.empty:
            if (component == 'solar_pv' or component == 'wind') and st.session_state[f'{component}_curtailment']:
                combined_energy = df[['UTC Time', f'Model {component} Used Energy Total [Wh]']]
            else:
                combined_energy = df[['UTC Time', f'Model {component} Energy Total [Wh]']]
        else:
            if (component == 'solar_pv' or component == 'wind') and st.session_state[f'{component}_curtailment']:
                combined_energy = combined_energy.merge(df[['UTC Time', f'Model {component} Used Energy Total [Wh]']], on='UTC Time')
            else:
                combined_energy = combined_energy.merge(df[['UTC Time', f'Model {component} Energy Total [Wh]']], on='UTC Time')
    combined_energy['Total Energy [Wh]'] = combined_energy.iloc[:, 2:].sum(axis=1)
    combined_energy['Total Energy [Wh]'] -= combined_energy['Model consumption Energy Total [Wh]']
    result_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"energy_balance.csv"
    combined_energy.to_csv(result_path, index=False)