import streamlit as st
import pandas as pd
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface
import datetime as dt
import pytz
import requests


def load_csv_data(uploaded_file, delimiter: str, decimal: str, parameter: str):
    """
    Load CSV data with given delimiter and decimal options.
    
    Args:
        uploaded_file: The uploaded CSV file.
        delimiter (str): The delimiter used in the CSV file.
        decimal (str): The decimal separator used in the CSV file.
        resource_name (Optional[str]): The name of the resource (used for column naming).
    
    Returns:
        Optional[pd.DataFrame]: The loaded DataFrame or None if an error occurred.
    """
    try:
        uploaded_file.seek(0)
        data = pd.read_csv(uploaded_file, delimiter=delimiter, decimal=decimal)
        data = data.apply(pd.to_numeric, errors='coerce')
        
        if len(data.columns) > 1:
            selected_column = st.selectbox(f"Select the column representing {parameter}", data.columns)
            data = data[[selected_column]]
        
        data.index = range(1, len(data) + 1)
        data.index.name = 'Periods'
        
        if data.empty:
            st.warning("No data found in the CSV file. Please check delimiter and decimal settings.")
        elif data.isnull().values.any():
            st.warning("Some values could not be converted to numeric. Please check the data.")
        else:
            st.success(f"Data loaded successfully using delimiter '{delimiter}' and decimal '{decimal}'")
        
        return data
    except Exception as e:
        st.error(f"Error during import of CSV data: {e}")
        return None
    
# Function to load and process time series data with time zones and format handling
def load_timeseries_csv_with_timezone(uploaded_file, delimiter: str, decimal: str, time_format: str, timezone: str):
    """
    Load CSV time-series data with given delimiter, decimal options, and convert the time column to UTC datetime.
    
    Args:
        uploaded_file: The uploaded CSV file.
        delimiter (str): The delimiter used in the CSV file.
        decimal (str): The decimal separator used in the CSV file.
        time_format (str): The format of the time column to parse datetime (e.g., '%Y-%m-%d %H:%M:%S').
        timezone (str): The time zone of the data (e.g., 'Europe/Berlin').
        parameter (str): The name of the data parameter (e.g., temperature or irradiation).
    
    Returns:
        Optional[pd.DataFrame]: The loaded DataFrame with time in UTC or None if an error occurred.
    """
    try:
        uploaded_file.seek(0)
        data = pd.read_csv(uploaded_file, delimiter=delimiter, decimal=decimal)
        
        if data.empty:
            st.warning("No data found in the CSV file. Please check the file.")
            return None
        
        # Select the time column
        time_column = st.selectbox(f"Select the column representing time:", data.columns)
        
        # Convert the time column to datetime using the provided format and time zone
        try:
            data[time_column] = pd.to_datetime(data[time_column], format=time_format, errors='coerce')
        except ValueError as e:
            st.error(f"Error in parsing time column: {e}")
            return None

        # Localize to the selected timezone and convert to UTC
        local_tz = pytz.timezone(timezone)
        time = data[time_column].apply(lambda x: local_tz.localize(x).astimezone(pytz.UTC))

        if time.empty:
            st.warning("No valid time series data found. Please check the CSV file.")
        else:
            st.success(f"Time loaded successfully for Time and converted to UTC.")

        return time
    
    except Exception as e:
        st.error(f"Error during import of time from CSV: {e}")
        return None


def render_time_format_timezone_selectors():
    # List of all available time zones with country names
    timezones_with_countries = ["Universal Time Coordinated - UTC"] 
    for country_code, timezones in pytz.country_timezones.items():
        country_name = pytz.country_names[country_code]
        for timezone in timezones:
            timezones_with_countries.append(f"{country_name} - {timezone}")

    # Common time formats to select from
    TIME_FORMATS = [
        "%Y-%m-%d",                # 2024-01-01
        "%Y-%m-%d %H:%M:%S",        # 2024-01-01 12:00:00
        "%d/%m/%Y",                 # 01/01/2024
        "%d/%m/%Y %H:%M",           # 01/01/2024 12:00
        "%m/%d/%Y",                 # 01/01/2024
        "%m/%d/%Y %H:%M:%S",        # 01/01/2024 12:00:00
        "%H:%M:%S",                 # 12:00:00
        "%Y-%m-%dT%H:%M:%S",        # 2024-01-01T12:00:00 (ISO format)
        "Other"                     # Allow user to enter a custom format
    ]

    # Select time format from common options
    time_format_choice = st.selectbox("Select the time format of the CSV file:", TIME_FORMATS, index=1)

    # If "Other" is selected, show a text input for custom time format
    if time_format_choice == "Other":
        time_format = st.text_input("Enter the custom time format:", value="%Y-%m-%d %H:%M:%S")
    else:
        time_format = time_format_choice

    # Select time zone from a comprehensive list with country names
    selected_timezone_with_country = st.selectbox("Select the time zone of the data (with country):", timezones_with_countries)

    # Extract just the timezone (without the country name)
    selected_timezone = selected_timezone_with_country.split(' - ')[1]

    # Show the selected values for debugging/confirmation
    st.write(f"Selected Time Format: {time_format}")
    st.write(f"Selected Timezone: {selected_timezone_with_country}")

    return time_format, selected_timezone

def download_pvgis_wind_data(lat, lon):
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
    tmy_df.rename(columns={'time(UTC)': 'UTC Time', 'WS10m': 'Wind Speed'}, inplace=True)
    tmy_df = tmy_df[['UTC Time', 'Wind Speed']]

    # Convert 'UTC Time' column to 'MM-DD HH:MM' format
    tmy_df['UTC Time'] = pd.to_datetime(tmy_df['UTC Time'], format='%Y%m%d:%H%M')
    tmy_df['UTC Time'] = tmy_df['UTC Time'].dt.strftime('%m-%d %H:%M')

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
        st.dataframe(wind_data.head(10))
        if st.button("Reupload Data"):
            st.session_state.wind_speed_data_uploaded = False

    else:
        # Dropdown menu to choose between uploading data or downloading from NASA
        data_source = st.selectbox(
            "Select Data Source",
            ("Upload your own data", "Download from PVGIS")
        )

        if data_source == "Upload your own data":
            # Dropdown for selecting the input type
            st.session_state.wind_selected_input_type = st.selectbox(
                "Chooses ",
                [
                    "Simple", 
                    "Complex"
                ]
            )


            uploaded_file, delimiter, decimal = csv_upload_interface(f"solar")
            if uploaded_file:
                with st.expander(f"Time", expanded=False):
                    time_format, timezone = render_time_format_timezone_selectors()
                    time_data = load_timeseries_csv_with_timezone(uploaded_file, delimiter, decimal, time_format, timezone)
                with st.expander(f"Data", expanded=False):
                    data_dict = {}
                    if st.session_state.wind_selected_input_type == "Simple":         
                        wind_data = load_csv_data(uploaded_file, delimiter, decimal, 'Wind Speed')
                        data_dict['Wind Speed'] = wind_data.values.flatten() if wind_data is not None else None
                    if st.session_state.wind_selected_input_type == "Complex": 
                        st.number_input(
                            "Height 1:", 
                            min_value=0.0, 
                            value=st.session_state.wind_Z1,  # This displays the value from `st.session_state`
                            key="wind_Z1"  # This associates the widget with `st.session_state.wind_Z1`
                        )

                        # Use the value directly from `st.session_state.wind_Z1`
                        windz1_data = load_csv_data(uploaded_file, delimiter, decimal, f'Wind Speed {st.session_state.wind_Z1}m')
                        data_dict[f'Wind Speed {st.session_state.wind_Z1}m'] = windz1_data.values.flatten() if windz1_data is not None else None
                        st.number_input(f"Height 0:",
                            min_value=0.0, 
                            value=st.session_state.wind_Z0,
                            key=f"wind_Z0"
                        )
                        windz0_data = load_csv_data(uploaded_file, delimiter, decimal, f'Wind Speed {st.session_state.wind_Z0}m')
                        data_dict[f'Wind Speed {st.session_state.wind_Z0}m'] = windz0_data.values.flatten() if windz0_data is not None else None
                        temperature_data = load_csv_data(uploaded_file, delimiter, decimal, 'Temperature')
                        data_dict['Temperature'] = temperature_data.values.flatten() if temperature_data is not None else None

                if time_data is not None and all(value is not None for value in data_dict.values()):
                    # Combine all data into a single DataFrame (for all elements)
                    wind_data = pd.DataFrame({
                        'UTC Time': time_data.values,
                        **data_dict  # Dynamically unpack the dictionary
                    })

                    # Display the shape of the full DataFrame
                    st.write(f'Shape of Dataframe: {wind_data.shape}')

                    # Display only the first 10 rows of the DataFrame in the UI
                    st.dataframe(wind_data.head(10))

                    # Button to save the full DataFrame
                    if st.button(f"Save Data for", key=f"save_solar_csv"):
                        save_wind_data(wind_data, project_name)
                        st.session_state.wind_speed_data_uploaded = True  # Set the flag to True since data is now uploaded
                        st.rerun()

        elif data_source == "Download from PVGIS":
            if st.button(f"Download Wind Data from PVGIS", key=f"download_wind_data"):
                with st.spinner('Downloading data from PVGIS...'):

                    st.session_state.wind_selected_input_type = 'Simple'

                    irradiation_data = download_pvgis_wind_data( 
                        lat=st.session_state.lat, 
                        lon=st.session_state.lon
                    )

                    save_wind_data(irradiation_data, project_name)
                    st.session_state.wind_speed_data_uploaded = True  # Set the flag to True since data is now uploaded
                    st.rerun()