import streamlit as st
import pandas as pd
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface
import datetime as dt
import pytz
import numpy as np
import re


def load_csv_data(uploaded_file, delimiter: str, decimal: str, parameter: str) -> pd.DataFrame:
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
        
        return data
    except Exception as e:
        st.error(f"Error during import of CSV data: {e}")
        return None
    
# Function to load and process time series data with time zones and format handling
def load_timeseries_csv_with_timezone(uploaded_file, delimiter: str, decimal: str, time_format: str, timezone: str) -> pd.Series:
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
            st.warning("No valid time series data found. Please check the format.")

        return time
    
    except Exception as e:
        st.error(f"Error during import of time from CSV: {e}")
        return None


def render_time_format_timezone_selectors() -> tuple:
    # List of all available time zones with country names
    timezones_with_countries = ["Universal Time Coordinated - UTC"]
    # Add all GMT time zones
    gmt_offsets = range(-12, 15)  # GMT-12 to GMT+14
    for offset in gmt_offsets:
        sign = "+" if offset >= 0 else "-"
        hours = abs(offset)
        timezones_with_countries.append(f"UTC Offset {sign}{hours:02d}:00")
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

    col1, col2 = st.columns(2)
    with col1:
        # Select time format from common options
        time_format_choice = st.selectbox("Select the time format of the CSV file:", TIME_FORMATS, index=1)

        # If "Other" is selected, show a text input for custom time format
        if time_format_choice == "Other":
            time_format = st.text_input("Enter the custom time format:", value="%Y-%m-%d %H:%M:%S")
        else:
            time_format = time_format_choice
        st.write(f"Selected Time Format: {time_format}")

    with col2:
        # Select time zone from a comprehensive list with country names
        selected_timezone_with_country = st.selectbox("Select the time zone of the data (with country):", timezones_with_countries)

        if "UTC Offset" in selected_timezone_with_country:
            match = re.search(r'[+-]\d+', selected_timezone_with_country)
            offset = int(match.group())
            offset = offset * (-1)
            selected_timezone = f"Etc/GMT{'+' if offset > 0 else ''}{offset}"
        else:
            # Extract just the timezone (without the country name)
            selected_timezone = selected_timezone_with_country.split(' - ')[1]
        st.write(f"Selected Timezone: {selected_timezone}")

    return time_format, selected_timezone

    
def save_data(resource_data: pd.DataFrame, project_name: str, resource_name: str) -> None:
    """Save the resource data to a CSV file."""    
    project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_{resource_name}.csv"
    resource_data.to_csv(project_folder_path, index=False)


def upload_model_output(resource) -> None:
    """Streamlit page for configuring renewable energy technology parameters."""
    st.title(f"Upload the model's {resource} output")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'upload_model_parameters')
    project_name = st.session_state.get("project_name")
    if st.session_state[f'{resource}_data_uploaded']:
        st.write("Data has been uploaded:")
        project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_{resource}.csv"
        data = pd.read_csv(project_folder_path)
        st.dataframe(data.head(10), hide_index=True)
        if st.button("Reupload Data"):
            st.session_state[f'{resource}_data_uploaded'] = False

    else:

        st.session_state[f'{resource}_model_output_scope'] = st.radio(f"Is the {resource} output defined per unit or in total?", ("Per Unit", "Total"))

        uploaded_file, delimiter, decimal = csv_upload_interface(f"energy_production_{resource}")
        if uploaded_file:
            with st.expander(f"Time", expanded=False):
                time_format, timezone = render_time_format_timezone_selectors()
                time_data = load_timeseries_csv_with_timezone(uploaded_file, delimiter, decimal, time_format, timezone)
            with st.expander(f"Data", expanded=False):
                data_dict = {}
    
                if st.session_state[f'{resource}_model_output_scope'] == "Total": 
                    col1, col2 = st.columns(2)
                    with col1:
                        energy_output_data = load_csv_data(uploaded_file, delimiter, decimal, f'Total {resource} Energy')
                    with col2:
                        unit = st.selectbox(
                            f"Select the unit of the {resource} output:",
                            ['Wh', 'kWh', 'MWh']
                        ) 
                    if unit == 'kWh':
                        energy_output_data = energy_output_data * 1e3
                    elif unit == 'MWh':
                        energy_output_data = energy_output_data * 1e6
                    data_dict[f'Model {resource} Energy Total [Wh]'] = energy_output_data.values.flatten() if energy_output_data is not None else None
                    if resource == "generator":
                        fuel_consumption_data = load_csv_data(uploaded_file, delimiter, decimal, 'Model Fuel Consumption Total [l]')
                        data_dict['Model Fuel Consumption Total [l]'] = fuel_consumption_data.values.flatten() if fuel_consumption_data is not None else None

                elif st.session_state[f'{resource}_model_output_scope'] == "Per Unit":
                    total_energy_output = None
                    total_fuel_consumption = None
                    for unit in range(st.session_state[f'{resource}_num_units']):
                        energy_output_data = load_csv_data(uploaded_file, delimiter, decimal, f'Model {resource} Energy Unit {unit + 1} [Wh]')
                        if energy_output_data is not None:
                            if unit == 'kWh':
                                energy_output_data = energy_output_data * 1e3
                            elif unit == 'MWh':
                                energy_output_data = energy_output_data * 1e6
                            data_dict[f'Model {resource} Energy Unit {unit + 1} [Wh]'] = energy_output_data.values.flatten()
                            # Sum element-wise using NumPy
                            if total_energy_output is None:
                                total_energy_output = energy_output_data.values.flatten()
                            else:
                                total_energy_output = np.add(total_energy_output, energy_output_data.values.flatten())

                        if resource == "generator":
                            fuel_consumption_data = load_csv_data(uploaded_file, delimiter, decimal, f'Model Fuel Consumption Unit {unit + 1} [l]')
                            if fuel_consumption_data is not None:
                                fuel_consumption_flattened = fuel_consumption_data.values.flatten()
                                data_dict[f'Model Fuel Consumption Unit {unit + 1} [l]'] = fuel_consumption_flattened
                                # Sum element-wise using NumPy
                                if total_fuel_consumption is None:
                                    total_fuel_consumption = fuel_consumption_flattened
                                else:
                                    total_fuel_consumption = np.add(total_fuel_consumption, fuel_consumption_flattened)

                    # Assign the total values after processing all units
                    data_dict[f'Model {resource} Energy Total [Wh]'] = total_energy_output
                    if resource == "generator":
                        data_dict[f'Model Fuel Consumption Total [Wh]'] = total_fuel_consumption

                # Combine all data into a DataFrame if time data and data dictionary are available
                if time_data is not None and all(value is not None for value in data_dict.values()):
                    # Combine all data into a single DataFrame (for all elements)
                    data = pd.DataFrame({
                        'UTC Time': time_data.values,
                        **{k: v for k, v in data_dict.items() if v is not None}  # Dynamically unpack the dictionary and filter None values
                    })

            # Display the shape of the full DataFrame
            st.write(f'Shape of Dataframe: {data.shape}')

            # Display only the first 10 rows of the DataFrame in the UI
            st.dataframe(data.head(10), hide_index=True)

            # Button to save the full DataFrame
            if st.button(f"Save Data for", key=f"save_solar_csv"):
                # Store the combined data in session state
                st.session_state[f'{resource}_data_uploaded'] = True  # Set the flag to True since data is now uploaded
                save_data(data, project_name, resource)
                st.rerun()