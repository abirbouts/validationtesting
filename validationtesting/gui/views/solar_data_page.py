"""
This file contains the code for the Solar Irradiation page in the GUI.
The user can upload their own solar irradiation data or download it from PVGIS.
"""

import streamlit as st
import pandas as pd
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface, time_format_selectors, load_csv_data, load_timeseries_csv
import datetime as dt
import requests

def download_pvgis_pv_data(lat, lon, timezone) -> pd.DataFrame:
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

    tmy_df['UTC Time'] = tmy_df['UTC Time'].astype(str)
    tmy_df['UTC Time'] = pd.to_datetime(tmy_df['UTC Time'], format='%Y%m%d:%H%M')
    # Force all dates to 2023 to remove leap year issues
    tmy_df['UTC Time'] = tmy_df['UTC Time'].apply(lambda x: x.replace(year=2023))
    tmy_df['UTC Time'] = tmy_df['UTC Time'].dt.tz_localize('UTC').dt.tz_convert(timezone)
    tmy_df['UTC Time'] = tmy_df['UTC Time'].apply(lambda x: x.replace(year=2023))
    tmy_df = tmy_df.sort_values(by='UTC Time')
    tmy_df['UTC Time'] = tmy_df['UTC Time'].dt.strftime('%m-%d %H:%M')
    tmy_df.rename(columns={'UTC Time': 'Time'}, inplace=True)

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
                    time_format = time_format_selectors()
                    time_data = load_timeseries_csv(uploaded_file, delimiter, decimal, time_format)
                with st.expander(f"Data", expanded=False):
                    data_dict = {}
                    if st.session_state.pv_temperature_dependent_efficiency:         
                        temperature_data = load_csv_data(uploaded_file, delimiter, decimal, 'Temperature (°C)')
                        data_dict['Temperature'] = temperature_data.values.flatten() if temperature_data is not None else None
                    GHI_data = load_csv_data(uploaded_file, delimiter, decimal, 'GHI [W/m^2]')
                    data_dict['GHI'] = GHI_data.values.flatten() if GHI_data is not None else None
                    DHI_data = load_csv_data(uploaded_file, delimiter, decimal, 'DHI [W/m^2]')
                    data_dict['DHI'] = DHI_data.values.flatten() if DHI_data is not None else None
                if time_data is not None and all(value is not None for value in data_dict.values()):
                    # Combine all data into a single DataFrame (for all elements)
                    irradiation_data = pd.DataFrame({
                        'Time': time_data.values,
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
                    
                    irradiation_data = download_pvgis_pv_data( 
                        lat=st.session_state.lat, 
                        lon=st.session_state.lon,
                        timezone=st.session_state.timezone
                    )

                    save_solar_irradiation_data(irradiation_data, project_name)
                    st.session_state.irradiation_data_uploaded = True  # Set the flag to True since data is now uploaded
                    st.rerun()
