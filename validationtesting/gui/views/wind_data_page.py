"""
This module contains the wind data upload page for the GUI. 
It allows the user to upload their own wind data or download it from PVGIS.
"""

import streamlit as st
import pandas as pd
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface, time_format_selectors, load_csv_data, load_timeseries_csv
import datetime as dt
import requests

def download_pvgis_wind_data(lat, lon, timezone) -> pd.DataFrame:
    """Download wind data from PVGIS API."""
    URL = 'https://re.jrc.ec.europa.eu/api/tmy?lat=' + str(lat) + '&lon=' + str(lon) + '&outputformat=json'

    # Make the request
    response = requests.get(URL)

    # Check the response status
    if response.status_code == 200:
        jsdata = response.json()  # Parse and return JSON data
    else:
        error_message = response.text  # Get the error message from the response
        st.error(f'Error while downloading from PVGIS. Error message: {error_message}')
        return None
    
    tmy_hourly_data = jsdata["outputs"]["tmy_hourly"]
    tmy_df = pd.DataFrame(tmy_hourly_data)
    st.write(tmy_df)
    # Rename columns
    tmy_df.rename(columns={'time(UTC)': 'UTC Time', 'WS10m': 'Wind Speed 10.0m [m/s]'}, inplace=True)
    tmy_df = tmy_df[['UTC Time', 'Wind Speed 10.0m [m/s]']]

    # Convert 'UTC Time' column to 'MM-DD HH:MM' format
    tmy_df['UTC Time'] = pd.to_datetime(tmy_df['UTC Time'], format='%Y%m%d:%H%M')
    # Force all dates to 2023 to remove leap year issues
    tmy_df['UTC Time'] = tmy_df['UTC Time'].apply(lambda x: x.replace(year=2023))
    tmy_df['UTC Time'] = tmy_df['UTC Time'].dt.tz_localize('UTC').dt.tz_convert(timezone).dt.strftime('%m-%d %H:%M')
    tmy_df.rename(columns={'UTC Time': 'Time'}, inplace=True)

    return tmy_df
    
def save_wind_data(resource_data: pd.DataFrame, project_name: str) -> None:
    project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / "wind_data.csv"
    resource_data.to_csv(project_folder_path, index=False)

def wind_data() -> None:
    """Streamlit page for configuring renewable energy technology parameters."""
    st.title("Upload Wind Data")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'wind_parameters')
    project_name = st.session_state.get("project_name")

    if st.session_state.wind_speed_data_uploaded == True:
        st.write("Data has been uploaded:")
        project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / "wind_data.csv"
        wind_data = pd.read_csv(project_folder_path)
        st.dataframe(wind_data.head(10), hide_index=True)
        if st.button("Reupload Data"):
            st.session_state.wind_speed_data_uploaded = False

    else:
        # Dropdown menu to choose between uploading data or downloading from NASA
        data_source = st.selectbox(
            "Select Data Source",
            ("Upload your own data", "Download from PVGIS")
        )

        if data_source == "Upload your own data":


            uploaded_file, delimiter, decimal = csv_upload_interface(f"solar")
            if uploaded_file:
                # Dropdown for selecting the input type
                st.session_state.wind_selected_input_type = st.selectbox(
                    "Chooses ",
                    [
                        "Wind Speed given for one Height", 
                        "Wind Speed given for two Heights"
                    ]
                )
                with st.expander(f"Time", expanded=False):
                    time_format = time_format_selectors()
                    time_data = load_timeseries_csv(uploaded_file, delimiter, decimal, time_format)
                with st.expander(f"Data", expanded=False):
                    data_dict = {}
                    if st.session_state.wind_selected_input_type == "Wind Speed given for one Height":
                        st.session_state.wind_Z1 = st.number_input(
                            "Height 1:", 
                            min_value=0.0, 
                            value=st.session_state.wind_Z1,  # This displays the value from `st.session_state`
                        )

                        wind_data = load_csv_data(uploaded_file, delimiter, decimal, f'Wind Speed {st.session_state.wind_Z1}m [m/s]')
                        data_dict[f'Wind Speed {st.session_state.wind_Z1}m [m/s]'] = wind_data.values.flatten() if wind_data is not None else None
                    if st.session_state.wind_selected_input_type == "Wind Speed given for two Heights": 
                        st.session_state.wind_Z1 = st.number_input(
                            "Height 1:", 
                            min_value=0.0, 
                            value=st.session_state.wind_Z1,  # This displays the value from `st.session_state`
                        )

                        # Use the value directly from `st.session_state.wind_Z1`
                        windz1_data = load_csv_data(uploaded_file, delimiter, decimal, f'Wind Speed {st.session_state.wind_Z1}m [m/s]')
                        data_dict[f'Wind Speed {st.session_state.wind_Z1}m [m/s]'] = windz1_data.values.flatten() if windz1_data is not None else None
                        st.session_state.wind_Z0 = st.number_input(f"Height 0:",
                            min_value=0.0, 
                            value=st.session_state.wind_Z0,
                        )
                        windz0_data = load_csv_data(uploaded_file, delimiter, decimal, f'Wind Speed {st.session_state.wind_Z0}m [m/s]')
                        data_dict[f'Wind Speed {st.session_state.wind_Z0}m [m/s]'] = windz0_data.values.flatten() if windz0_data is not None else None
                        temperature_data = load_csv_data(uploaded_file, delimiter, decimal, 'Temperature [°C]')
                        data_dict['Temperature [°C]'] = temperature_data.values.flatten() if temperature_data is not None else None

                if time_data is not None and all(value is not None for value in data_dict.values()):
                    # Combine all data into a single DataFrame (for all elements)
                    wind_data = pd.DataFrame({
                        'Time': time_data.values,
                        **data_dict  # Dynamically unpack the dictionary
                    })

                    # Display the shape of the full DataFrame
                    st.write(f'Shape of Dataframe: {wind_data.shape}')

                    # Display only the first 10 rows of the DataFrame in the UI
                    st.dataframe(wind_data.head(10), hide_index=True)

                    # Button to save the full DataFrame
                    if st.button(f"Save Data for", key=f"save_solar_csv"):
                        save_wind_data(wind_data, project_name)
                        st.session_state.wind_speed_data_uploaded = True  # Set the flag to True since data is now uploaded
                        st.rerun()

        elif data_source == "Download from PVGIS":
            surface_options = ["Very smooth, ice or mud",
                                "Snow surface", 
                                "Lawn grass", 
                                "Rough pasture", 
                                "Fallow field",
                                "Crops",
                                "Few Trees",
                                "Many trees, hedges, few buildings",
                                "Forest and woodlands",
                                "Suburbs",
                                "Centers of cities with tall buildings"]
            surface_roughnesses = [0.00001, 0.003, 0.008, 0.01, 0.03, 0.05, 0.10, 0.25, 0.50, 1.50, 3.00]

            st.session_state.wind_surface_type = st.selectbox(
                "Surface Type:",
                options=surface_options,
                index=surface_options.index(st.session_state.wind_surface_type) if st.session_state.wind_surface_type in surface_options else 0, 
                help="Select the type of surface where the wind turbine is installed. This affects the wind speed profile.")

            st.session_state.wind_surface_roughness = surface_roughnesses[surface_options.index(st.session_state.wind_surface_type)]

            if st.button(f"Download Wind Data from PVGIS", key=f"download_wind_data"):
                with st.spinner('Downloading data from PVGIS...'):

                    st.session_state.wind_selected_input_type = "Wind Speed given for one Height"
                    st.session_state.wind_Z1 = 10.0

                    wind_data = download_pvgis_wind_data( 
                        lat=st.session_state.lat,
                        lon=st.session_state.lon,
                        timezone=st.session_state.timezone
                    )

                    save_wind_data(wind_data, project_name)
                    st.session_state.wind_speed_data_uploaded = True  # Set the flag to True since data is now uploaded
                    st.rerun()