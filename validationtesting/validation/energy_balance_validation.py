"""
This module is used to validate the energy balance of the system.
"""

import streamlit as st
import pandas as pd
from config.path_manager import PathManager

def energy_balance_validation() -> None:
    """Calculate the energy balance of the system and save the result in a CSV file."""
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
    if st.session_state.conversion:
        used_components.append("conversion")

    combined_energy = pd.DataFrame()
    for component in used_components:
        if not component == "conversion":
            project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_{component}.csv"
            df = pd.read_csv(project_folder_path)
            if combined_energy.empty:
                if (component == 'solar_pv' or component == 'wind') and st.session_state[f'{component}_curtailment']:
                    combined_energy = df[['Time', f'Model {component} Energy Total [Wh]', f'Model {component} Curtailed Energy Total [Wh]']]
                    combined_energy[f'Model {component} Used Energy Total [Wh]'] = combined_energy[f'Model {component} Energy Total [Wh]'] - combined_energy[f'Model {component} Curtailed Energy Total [Wh]']
                    combined_energy.drop(columns=[f'Model {component} Energy Total [Wh]', f'Model {component} Curtailed Energy Total [Wh]'], inplace=True)
                else:
                    combined_energy = df[['Time', f'Model {component} Energy Total [Wh]']]
            else:
                if (component == 'solar_pv' or component == 'wind') and st.session_state[f'{component}_curtailment']:
                    combined_energy = combined_energy.merge(df[['Time', f'Model {component} Energy Total [Wh]', f'Model {component} Curtailed Energy Total [Wh]']], on='Time')
                    combined_energy[f'Model {component} Used Energy Total [Wh]'] = combined_energy[f'Model {component} Energy Total [Wh]'] - combined_energy[f'Model {component} Curtailed Energy Total [Wh]']
                    combined_energy.drop(columns=[f'Model {component} Energy Total [Wh]', f'Model {component} Curtailed Energy Total [Wh]'], inplace=True)
                else:
                    combined_energy = combined_energy.merge(df[['Time', f'Model {component} Energy Total [Wh]']], on='Time')
    
    # Add this before Total Energy
    if "conversion" in used_components:
        combined_energy['Conversion Losses [Wh]'] = 0

    combined_energy['Total Energy [Wh]'] = combined_energy.iloc[:, 2:].sum(axis=1)

    if "conversion" in used_components:
        conversion_losses_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "conversion_losses_validation.csv"
        conversion_losses = pd.read_csv(conversion_losses_path)
        combined_energy['Conversion Losses [Wh]'] = conversion_losses.loc[:, conversion_losses.columns.str.contains('Conversion Losses')].sum(axis=1)
        combined_energy['Total Energy [Wh]'] -= combined_energy['Conversion Losses [Wh]']

    combined_energy['Total Energy [Wh]'] -= combined_energy['Model consumption Energy Total [Wh]']
    result_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"energy_balance.csv"
    combined_energy.to_csv(result_path, index=False)