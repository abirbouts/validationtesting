"""
This module contains the Streamlit page for uploading the model's output data.
"""

import streamlit as st
import pandas as pd
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface, time_format_selectors, load_csv_data, load_timeseries_csv
import numpy as np
    
def save_data(resource_data: pd.DataFrame, project_name: str) -> None:
    """Save the resource data to a CSV file."""    
    project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_conversion_losses.csv"
    resource_data.to_csv(project_folder_path, index=False)


def upload_conversion_losses() -> None:
    """Streamlit page for uploading the model's output data."""
    
    st.title(f"Upload the model's conversion losses")
    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'conversion_parameters')
    project_name = st.session_state.get("project_name")

    # Check if data has been uploaded and show it
    if st.session_state.conversion_losses_data_uploaded:
        st.write("Data has been uploaded:")
        project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_conversion_losses.csv"
        data = pd.read_csv(project_folder_path)
        st.dataframe(data.head(24), hide_index=True)       
        if st.button("Reupload Data"):
            st.session_state.conversion_losses_data_uploaded = False

    # Upload interface
    else:
        uploaded_file, delimiter, decimal = csv_upload_interface(f"model_conversion_losses")
        if uploaded_file:
            # Select Time column
            with st.expander(f"Time", expanded=False):
                time_format = time_format_selectors()
                time_data = load_timeseries_csv(uploaded_file, delimiter, decimal, time_format)
            with st.expander(f"Data", expanded=False):
                data_dict = {}
                if st.session_state.solar_pv and st.session_state.solar_pv_connection_type == "Connected with a seperate Inverter to the Microgrid":
                    col1, col2 = st.columns(2)
                    with col1:
                        solar_pv_losses = load_csv_data(uploaded_file, delimiter, decimal, f'Solar PV Conversion Losses [Wh]')
                    with col2:
                        energy_unit = st.selectbox(
                            f"Select the unit of the output:",
                            ['Wh', 'kWh', 'MWh']
                        ) 
                    if energy_unit == 'kWh':
                        solar_pv_losses = solar_pv_losses * 1e3
                    elif energy_unit == 'MWh':
                        solar_pv_losses = solar_pv_losses * 1e6
                    data_dict[f'solar_pv Conversion Losses [Wh]'] = solar_pv_losses.values.flatten() if solar_pv_losses is not None else None
                
                if st.session_state.wind and st.session_state.wind_connection_type == "Connected with a AC-AC Converter to the Microgrid":
                    col1, col2 = st.columns(2)
                    with col1:
                        wind_losses = load_csv_data(uploaded_file, delimiter, decimal, f'Wind Conversion Losses [Wh]')
                    with col2:
                        energy_unit = st.selectbox(
                            f"Select the unit of the output:",
                            ['Wh', 'kWh', 'MWh']
                        ) 
                    if energy_unit == 'kWh':
                        wind_losses = wind_losses * 1e3
                    elif energy_unit == 'MWh':
                        wind_losses = wind_losses * 1e6
                    data_dict[f'wind Conversion Losses [Wh]'] = wind_losses.values.flatten() if wind_losses is not None else None
                
                if st.session_state.generator and st.session_state.current_type == "Direct Current":
                    col1, col2 = st.columns(2)
                    with col1:
                        generator_losses = load_csv_data(uploaded_file, delimiter, decimal, f'Generator Conversion Losses [Wh]')
                    with col2:
                        energy_unit = st.selectbox(
                            f"Select the unit of the output:",
                            ['Wh', 'kWh', 'MWh']
                        )
                    if energy_unit == 'kWh':
                        generator_losses = generator_losses * 1e3
                    elif energy_unit == 'MWh':
                        generator_losses = generator_losses * 1e6
                    data_dict[f'generator Conversion Losses [Wh]'] = generator_losses.values.flatten() if generator_losses is not None else None
                
                if st.session_state.battery and st.session_state.current_type == "Alternating Current":
                    if st.session_state.solar_pv and st.session_state.solar_pv_connection_type == "Connected with the same Inverter as the Battery to the Microgrid":
                        system = "DC System"
                    else:
                        system = "battery"
                    col1, col2 = st.columns(2)
                    with col1:
                        battery_losses = load_csv_data(uploaded_file, delimiter, decimal, f'{system} Conversion Losses [Wh]')
                    with col2:
                        energy_unit = st.selectbox(
                            f"Select the unit of the output:",
                            ['Wh', 'kWh', 'MWh']
                        )
                    if energy_unit == 'kWh':
                        battery_losses = battery_losses * 1e3
                    elif energy_unit == 'MWh':
                        battery_losses = battery_losses * 1e6
                    data_dict[f'{system} Conversion Losses [Wh]'] = battery_losses.values.flatten() if battery_losses is not None else None


                # Combine all data into a DataFrame if time data and data dictionary are available
                if time_data is not None and all(value is not None for value in data_dict.values()):
                    # Combine all data into a single DataFrame (for all elements)
                    data = pd.DataFrame({
                        'Time': time_data.values,
                        **{k: v for k, v in data_dict.items() if v is not None}  # Dynamically unpack the dictionary and filter None values
                    })

            # Display the shape of the full DataFrame
            st.write(f'Shape of Dataframe: {data.shape}')

            # Display only the first 10 rows of the DataFrame in the UI
            st.dataframe(data.head(10), hide_index=True)

            # Button to save the full DataFrame
            if st.button(f"Save Data for", key=f"save_conversion_losses"):
                st.session_state.conversion_losses_data_uploaded = True  # Set the flag to True since data is now uploaded
                save_data(data, project_name)
                st.rerun()