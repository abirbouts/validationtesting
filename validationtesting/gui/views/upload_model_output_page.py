"""
This module contains the Streamlit page for uploading the model's output data.
"""

import streamlit as st
import pandas as pd
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface, time_format_selectors, load_csv_data, load_timeseries_csv
import numpy as np
    
def save_data(resource_data: pd.DataFrame, project_name: str, resource_name: str) -> None:
    """Save the resource data to a CSV file."""    
    project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_{resource_name}.csv"
    resource_data.to_csv(project_folder_path, index=False)


def upload_model_output(resource) -> None:
    """Streamlit page for uploading the model's output data."""
    
    st.title(f"Upload the model's {resource} output")
    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'upload_model_parameters')
    project_name = st.session_state.get("project_name")
    
    # Check if data has been uploaded and show it
    if st.session_state[f'{resource}_data_uploaded']:
        st.write("Data has been uploaded:")
        project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_{resource}.csv"
        data = pd.read_csv(project_folder_path)
        st.dataframe(data.head(24), hide_index=True)
        if resource == "generator":
            if st.session_state.generator_fuel_consumption_scope[0] == "Total": 
                st.write(f"Total fuel consumption: {st.session_state.generator_total_fuel_consumption[0]} l")
                    
        if st.button("Reupload Data"):
            st.session_state[f'{resource}_data_uploaded'] = False

    # Upload interface
    else:
        uploaded_file, delimiter, decimal = csv_upload_interface(f"energy_production_{resource}")
        if uploaded_file:
            # Select Time column
            with st.expander(f"Time", expanded=False):
                time_format = time_format_selectors()
                time_data = load_timeseries_csv(uploaded_file, delimiter, decimal, time_format)
            with st.expander(f"Data", expanded=False):
                data_dict = {}

                # Select Energy Production
                col1, col2 = st.columns(2)
                with col1:
                    energy_output_data = load_csv_data(uploaded_file, delimiter, decimal, f'Total {resource} Energy')
                with col2:
                    energy_unit = st.selectbox(
                        f"Select the unit of the {resource} output:",
                        ['Wh', 'kWh', 'MWh']
                    ) 
                if energy_unit == 'kWh':
                    energy_output_data = energy_output_data * 1e3
                elif energy_unit == 'MWh':
                    energy_output_data = energy_output_data * 1e6
                data_dict[f'Model {resource} Energy Total [Wh]'] = energy_output_data.values.flatten() if energy_output_data is not None else None
                if resource == "solar_pv" or resource == "wind":
                    if st.session_state[f'{resource}_curtailment'][0]:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.session_state[f'{resource}_curtailment'][0] = st.toggle("Curtailment", value=st.session_state[f'{resource}_curtailment'][0])
                        with col2:
                                curtailment_data = load_csv_data(uploaded_file, delimiter, decimal, f'Curtailed {resource} Energy')
                                if energy_unit == 'kWh':
                                    curtailment_data = curtailment_data * 1e3
                                elif energy_unit == 'MWh':
                                    curtailment_data = curtailment_data * 1e6
                                data_dict[f'Model {resource} Curtailed Energy Total [Wh]'] = curtailment_data.values.flatten() if curtailment_data is not None else None
                # Select Fuel Consumption
                if resource == "generator":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.session_state.generator_fuel_consumption_scope[0] = st.selectbox(
                            f"Select in what scope the fuel consumption is given:",
                            ['Total', 'Time Series']
                        ) 
                    with col2:
                        if st.session_state.generator_fuel_consumption_scope[0] == 'Total':
                            st.session_state.generator_total_fuel_consumption[0] = st.number_input(f"Enter the total fuel consumption [l]:", value=0.0)
                        if st.session_state.generator_fuel_consumption_scope[0] == 'Time Series':
                            fuel_consumption_data = load_csv_data(uploaded_file, delimiter, decimal, 'Model Fuel Consumption Total [l]')
                            data_dict['Model Fuel Consumption Total [l]'] = fuel_consumption_data.values.flatten() if fuel_consumption_data is not None else None


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
            if st.button(f"Save Data for", key=f"save_solar_csv"):
                st.session_state[f'{resource}_data_uploaded'] = True  # Set the flag to True since data is now uploaded
                save_data(data, project_name, resource)
                st.rerun()