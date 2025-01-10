"""
This file contains the code for the Solar Irradiation page in the GUI.
The user can upload their own solar irradiation data or download it from PVGIS.
"""

import streamlit as st
import pandas as pd
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface, time_format_timezone_selectors, load_csv_data, load_timeseries_csv_with_timezone
import datetime as dt
import requests

def download_pvgis_pv_data(lat, lon) -> pd.DataFrame:
    """
    Function to download solar irradiation data from PVGIS.
    """
    URL = 'https://re.jrc.ec.europa.eu/api/tmy?lat=' + str(lat) + '&lon=' + str(lon) + '&outputformat=json'
    # Make the request
    response = requests.get(URL)

    # Check the response status
    if response.status_code == 200:
        jsdata = response.json()  # Parse and return JSON data
    else:
        error_message = response.text  # Get the error message from the response
        st.error(f'Error Wile downloading from PVGIS. Error message: {error_message}')
        return None
    
    tmy_hourly_data = jsdata["outputs"]["tmy_hourly"]
    tmy_df = pd.DataFrame(tmy_hourly_data)

    # Rename columns
    tmy_df.rename(columns={'time(UTC)': 'UTC Time', 'T2m': 'Temperature [°C]', 'G(h)': 'GHI [W/m^2]', 'Gd(h)': 'DHI [W/m^2]'}, inplace=True)
    tmy_df = tmy_df[['UTC Time', 'Temperature [°C]', 'GHI [W/m^2]', 'DHI [W/m^2]']]

    # Convert 'UTC Time' column to 'MM-DD HH:MM' format
    tmy_df['UTC Time'] = pd.to_datetime(tmy_df['UTC Time'], format='%Y%m%d:%H%M')
    tmy_df['UTC Time'] = tmy_df['UTC Time'].dt.strftime('%m-%d %H:%M')

    return tmy_df


def save_solar_irradiation_data(resource_data: pd.DataFrame, project_name: str) -> None:
    """
    Save data to a CSV file in the project's inputs folder.
    """
    project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / "solar_irradiation.csv"
    resource_data.to_csv(project_folder_path, index=False)

def irradiation_data() -> None:
    """
    Streamlit page for uploading solar irradiation data.
    """
    st.title("Solar Irradiation")
    st.subheader("Upload the model's solar PV output")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'solar_irradiation_parameters')
    project_name = st.session_state.get("project_name")

    # Check if data has been uploaded and show the data 
    if st.session_state.irradiation_data_uploaded == True:
        st.write("Data has been uploaded:")
        project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / "solar_irradiation.csv"
        irradiation_data = pd.read_csv(project_folder_path)
        st.dataframe(irradiation_data.head(10), hide_index=True)
        if st.button("Reupload Data"):
            st.session_state.irradiation_data_uploaded = False

    else:
        # Dropdown menu to choose between uploading data or downloading from NASA
        data_source = st.selectbox(
            "Select Data Source",
            ("Upload your own data", "Download from PVGIS")
        )

        # Upload interface
        if data_source == "Upload your own data":
            uploaded_file, delimiter, decimal = csv_upload_interface(f"solar")
            if uploaded_file:
                with st.expander(f"Time", expanded=False):
                    time_format, timezone = time_format_timezone_selectors()
                    time_data = load_timeseries_csv_with_timezone(uploaded_file, delimiter, decimal, time_format, timezone)
                with st.expander(f"Data", expanded=False):
                                # Dropdown for selecting the input type
                    st.session_state.selected_input_type = st.selectbox(
                        "Select Input Type",
                        [
                            "GHI & DHI", 
                            "DHI & DNI", 
                            "Total Irradiance"
                        ]
                    )

                    # Based on the selected input type, adjust the upload options and store in session state
                    if st.session_state.selected_input_type == "GHI & DHI":
                        st.session_state.Input_GHI = True
                        st.session_state.Input_DHI = True
                        st.session_state.Input_DNI = False
                        st.session_state.Input_G_total = False

                    elif st.session_state.selected_input_type == "DHI & DNI":
                        st.session_state.Input_GHI = False
                        st.session_state.Input_DHI = True
                        st.session_state.Input_DNI = True
                        st.session_state.Input_G_total = False

                    elif st.session_state.selected_input_type == "Total Irradiance":
                        st.session_state.Input_GHI = False
                        st.session_state.Input_DHI = False
                        st.session_state.Input_DNI = False
                        st.session_state.Input_G_total = True
                    data_dict = {}
                    if st.session_state.pv_temperature_dependent_efficiency:         
                        temperature_data = load_csv_data(uploaded_file, delimiter, decimal, 'Temperature (°C)')
                        data_dict['Temperature'] = temperature_data.values.flatten() if temperature_data is not None else None
                    if st.session_state.Input_GHI:
                        GHI_data = load_csv_data(uploaded_file, delimiter, decimal, 'GHI [W/m^2]')
                        data_dict['GHI'] = GHI_data.values.flatten() if GHI_data is not None else None
                    if st.session_state.Input_DHI:
                        DHI_data = load_csv_data(uploaded_file, delimiter, decimal, 'DHI [W/m^2]')
                        data_dict['DHI'] = DHI_data.values.flatten() if DHI_data is not None else None
                    if st.session_state.Input_DNI:
                        DNI_data = load_csv_data(uploaded_file, delimiter, decimal, 'DNI [W/m^2]')
                        data_dict['DNI'] = DNI_data.values.flatten() if DNI_data is not None else None
                    if st.session_state.Input_G_total:
                        solar_pv_types = st.session_state.get("solar_pv_types")
                        for type in solar_pv_types:
                            G_total_data = load_csv_data(uploaded_file, delimiter, decimal, f'Total Irradiance {type} [W/m^2]')
                            data_dict[f'G Total {type} [W/m^2]'] = G_total_data.values.flatten() if G_total_data is not None else None
                if time_data is not None and all(value is not None for value in data_dict.values()):
                    # Combine all data into a single DataFrame (for all elements)
                    irradiation_data = pd.DataFrame({
                        'UTC Time': time_data.values,
                        **data_dict 
                    })

                    # Display the shape of the full DataFrame
                    st.write(f'Shape of Dataframe: {irradiation_data.shape}')

                    # Display only the first 10 rows of the DataFrame in the UI
                    st.dataframe(irradiation_data.head(10), hide_index=True)

                    # Button to save the full DataFrame
                    if st.button(f"Save Data for", key=f"save_solar_csv"):
                        save_solar_irradiation_data(irradiation_data, project_name)
                        st.session_state.irradiation_data_uploaded = True  # Set the flag to True since data is now uploaded
                        st.rerun()
        
        # Download data from PVGIS
        elif data_source == "Download from PVGIS":
            if st.button(f"Download Solar Data from PVGIS", key=f"download_solar_data"):
                with st.spinner('Downloading data from PVGIS...'):

                    st.session_state.Input_GHI = True
                    st.session_state.Input_DHI = True
                    st.session_state.Input_DNI = False
                    st.session_state.Input_G_total = False

                    irradiation_data = download_pvgis_pv_data( 
                        lat=st.session_state.lat, 
                        lon=st.session_state.lon
                    )

                    save_solar_irradiation_data(irradiation_data, project_name)
                    st.session_state.irradiation_data_uploaded = True  # Set the flag to True since data is now uploaded
                    st.rerun()
