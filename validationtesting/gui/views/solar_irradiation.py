import streamlit as st
import pandas as pd
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface
import datetime as dt
import pytz

def ensure_list_length(key: str, length: int) -> None:
    """Ensure the list in session state has the required length."""
    if key not in st.session_state:
        st.session_state[key] = [0.0] * length
    else:
        st.session_state[key].extend([0.0] * (length - len(st.session_state[key])))

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

    
def save_solar_irradiation_data(resource_data: pd.DataFrame, project_name: str) -> None:
    project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / "solar_irradiation.csv"
    resource_data.to_csv(project_folder_path, index=True)
    st.success(f"Resource data saved successfully at {project_folder_path}")


def update_parameters(i: int, res_name: str, time_horizon: int, brownfield: bool, land_availability: float, currency: str) -> None:
    """Update renewable parameters for the given index."""
    st.subheader(f"{res_name} Parameters")
    
    st.session_state.res_inverter_efficiency[i] = st.number_input(
        f"Inverter Efficiency [%]", 
        min_value=0.0, 
        max_value=100.0, 
        value=float(st.session_state.res_inverter_efficiency[i] * 100), 
        key=f"inv_eff_{i}") / 100
    
    if land_availability > 0:
        st.session_state.res_specific_area[i] = st.number_input(
            f"Specific Area [m2/kW]",
            min_value=0.0, 
            value=float(st.session_state.res_specific_area[i]), 
            key=f"spec_area_{i}")
    
    st.session_state.res_specific_investment_cost[i] = st.number_input(
        f"Specific Investment Cost [{currency}/W]", 
        min_value=0.0,
        value=float(st.session_state.res_specific_investment_cost[i]), 
        key=f"inv_cost_{i}")
    
    st.session_state.res_specific_om_cost[i] = st.number_input(
        f"Specific O&M Cost as % of investment cost [%]", 
        min_value=0.0, 
        max_value=100.0,
        value=float(st.session_state.res_specific_om_cost[i] * 100), 
        key=f"om_cost_{i}") / 100
    
    if brownfield:
        st.session_state.res_lifetime[i] = st.number_input(
            f"Lifetime [years]", 
            value=float(st.session_state.res_lifetime[i]), 
            key=f"lifetime_{i}")
    else:
        st.session_state.res_lifetime[i] = st.number_input(
            f"Lifetime [years]", 
            min_value=float(time_horizon), 
            value=max(float(time_horizon), float(st.session_state.res_lifetime[i])), 
            key=f"lifetime_{i}")
    
    st.session_state.res_unit_co2_emission[i] = st.number_input(
        f"Unit CO2 Emission [kgCO2/W]", 
        value=float(st.session_state.res_unit_co2_emission[i]), 
        key=f"co2_{i}")

    if brownfield:
        st.write("##### Brownfield project parameters:")
        st.session_state.res_existing_capacity[i] = st.number_input(
            f"Existing Capacity [kW]", 
            min_value=0.0,
            value=float(st.session_state.res_existing_capacity[i]) * 1000, 
            key=f"exist_cap_{i}") / 1000
        st.session_state.res_existing_years[i] = st.number_input(
            f"Existing Years [years]", 
            min_value=0,
            max_value=(st.session_state.res_lifetime[i] - 1),
            value=float(st.session_state.res_existing_years[i]), 
            key=f"exist_years_{i}")

def solar_irradiation() -> None:
    """Streamlit page for configuring renewable energy technology parameters."""
    st.title("Solar Irradiation")
    st.subheader("Upload the model's solar PV output")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'solar_irradiation_parameters')
    project_name = st.session_state.get("project_name")

    if st.session_state.irradiation_data_uploaded == True:
        st.write("Data has already been uploaded:")
        project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / "solar_irradiation.csv"
        irradiation_data = pd.read_csv(project_folder_path)
        st.dataframe(irradiation_data.head(10))
        if st.button("Reupload Data"):
            st.session_state.irradiation_data_uploaded = False

    else:
        # Dropdown menu to choose between uploading data or downloading from NASA
        data_source = st.selectbox(
            "Select Data Source",
            ("Upload your own data", "Download from NASA")
        )

        # Set up input types based on session state
        if "Input_G_total" not in st.session_state:
            st.session_state.Input_G_total = False
        if "Input_GHI" not in st.session_state:
            st.session_state.Input_GHI = False
        if "Input_DHI" not in st.session_state:
            st.session_state.Input_DHI = False
        if "Input_DNI" not in st.session_state:
            st.session_state.Input_DNI = False
        if "data_uploaded" not in st.session_state:
            st.session_state.data_uploaded = False  # New flag to track upload status

        if data_source == "Upload your own data":
            # Dropdown for selecting the input type
            st.session_state.selected_input_type = st.selectbox(
                "Select Input Type",
                [
                    "GHI & DHI", 
                    "DHI & DNI", 
                    "GHI (Calculating rest with Erbs etc.)", 
                    "Total Irradiance"
                ]
            )

            # Based on the selected input type, adjust the options or store in session state
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

            elif st.session_state.selected_input_type == "GHI (Calculating rest with Erbs etc.)":
                st.session_state.Input_GHI = True
                st.session_state.Input_DHI = False
                st.session_state.Input_DNI = False
                st.session_state.Input_G_total = False

            elif st.session_state.selected_input_type == "Total Irradiance":
                st.session_state.Input_GHI = False
                st.session_state.Input_DHI = False
                st.session_state.Input_DNI = False
                st.session_state.Input_G_total = True

        elif data_source == "Download from NASA":
            # Placeholder or code for NASA data download
            st.write("Downloading data from NASA...")

        uploaded_file, delimiter, decimal = csv_upload_interface(f"solar")
        if uploaded_file:
            with st.expander(f"Time", expanded=False):
                time_format, timezone = render_time_format_timezone_selectors()
                time_data = load_timeseries_csv_with_timezone(uploaded_file, delimiter, decimal, time_format, timezone)
            with st.expander(f"Data", expanded=False):
                data_dict = {}
                if st.session_state.pv_temperature_dependent_efficiency:         
                    temperature_data = load_csv_data(uploaded_file, delimiter, decimal, 'Temperature')
                    data_dict['Temperature'] = temperature_data.values.flatten() if temperature_data is not None else None
                if st.session_state.Input_GHI:
                    GHI_data = load_csv_data(uploaded_file, delimiter, decimal, 'GHI')
                    data_dict['GHI'] = GHI_data.values.flatten() if GHI_data is not None else None
                if st.session_state.Input_DHI:
                    DHI_data = load_csv_data(uploaded_file, delimiter, decimal, 'DHI')
                    data_dict['DHI'] = DHI_data.values.flatten() if DHI_data is not None else None
                if st.session_state.Input_DNI:
                    DNI_data = load_csv_data(uploaded_file, delimiter, decimal, 'DNI')
                    data_dict['DNI'] = DNI_data.values.flatten() if DNI_data is not None else None
                if st.session_state.Input_G_total:
                    solar_pv_types = st.session_state.get("solar_pv_types")
                    for type in solar_pv_types:
                        G_total_data = load_csv_data(uploaded_file, delimiter, decimal, f'Total Irradiance {type}')
                        data_dict[f'G_Total_{type}'] = G_total_data.values.flatten() if G_total_data is not None else None
            if time_data is not None and all(value is not None for value in data_dict.values()):
                # Combine all data into a single DataFrame (for all elements)
                irradiation_data = pd.DataFrame({
                    'UTC Time': time_data.values,
                    **data_dict  # Dynamically unpack the dictionary
                })

                # Display the shape of the full DataFrame
                st.write(f'Shape of Dataframe: {irradiation_data.shape}')

                # Display only the first 10 rows of the DataFrame in the UI
                st.dataframe(irradiation_data.head(10))

                # Button to save the full DataFrame
                if st.button(f"Save Data for", key=f"save_solar_csv"):
                    save_solar_irradiation_data(irradiation_data, project_name)
                    st.session_state.irradiation_data_uploaded = True  # Set the flag to True since data is now uploaded