import streamlit as st
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface
import datetime as dt
import pytz
import pandas as pd
import numpy as np

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
        else:
            st.success(f"Data loaded successfully using delimiter '{delimiter}' and decimal '{decimal}'")
        
        return data
    except Exception as e:
        st.error(f"Error during import of CSV data: {e}")
        return None
    

@st.dialog("Enter Battery Specifications")
def enter_specifications(i: int) -> None:
    st.write(f"Enter Battery Specifications for Type {i+1}.")

    # Initialize wind_lifetime if necessary
    if len(st.session_state.wind_lifetime) < st.session_state.num_wind_types:
        st.session_state.wind_lifetime.extend([0] * (st.session_state.num_wind_types - len(st.session_state.wind_lifetime)))
    st.session_state.wind_lifetime[i] = st.number_input(f"Lifetime [in years]:", 
        min_value=0, 
        value=st.session_state.wind_lifetime[i],
        key=f"wind_lifetime_{i}"
    )

    # Initialize wind_rated_power if necessary
    if len(st.session_state.wind_rated_power) < st.session_state.num_wind_types:
        st.session_state.wind_rated_power.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_rated_power)))
    st.session_state.wind_rated_power[i] = st.number_input(f"Rated Power [W]:", 
        min_value=0.0, 
        value=st.session_state.wind_rated_power[i],
        key=f"wind_rated_power_{i}"
    )

    # Initialize wind_drivetrain_efficiency if necessary
    if len(st.session_state.wind_drivetrain_efficiency) < st.session_state.num_wind_types:
        st.session_state.wind_drivetrain_efficiency.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_drivetrain_efficiency)))
    st.session_state.wind_drivetrain_efficiency[i] = st.number_input(f"Drive Train Efficiency [%]:", 
        min_value=0.0,
        value=st.session_state.wind_drivetrain_efficiency[i],
        key=f"wind_drivetrain_efficiency_{i}"
    )
    st.session_state.wind_inverter_efficiency = [98.0]
    # Initialize wind_inverter_efficiency if necessary
    if len(st.session_state.wind_inverter_efficiency) < st.session_state.num_wind_types:
        st.session_state.wind_inverter_efficiency.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_inverter_efficiency)))
    st.session_state.wind_inverter_efficiency[i] = st.number_input(f"Inverter Efficiency [%]:", 
        min_value=0.0,
        value=st.session_state.wind_inverter_efficiency[i],
        key=f"wind_inverter_efficiency_{i}"
    )

    # Initialize wind_hub_height if necessary
    if len(st.session_state.wind_hub_height) < st.session_state.num_wind_types:
        st.session_state.wind_hub_height.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_hub_height)))
    st.session_state.wind_hub_height[i] = st.number_input(f"Hub Height [m]:", 
        min_value=0.0, 
        value=st.session_state.wind_hub_height[i],
        key=f"wind_hub_height_{i}"
    )

    if st.session_state.wind_temporal_degradation:
        # Initialize wind_temporal_degradation_rate if necessary
        if len(st.session_state.wind_temporal_degradation_rate) < st.session_state.num_wind_types:
            st.session_state.wind_temporal_degradation_rate.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_temporal_degradation_rate)))
        st.session_state.wind_temporal_degradation_rate[i] = st.number_input(
            f"Degradation Rate [%/year]:", 
            min_value=0.0, 
            value=st.session_state.wind_temporal_degradation_rate[i],
            key=f"wind_degradation_rate_{i}"
        )

    project_name = st.session_state.get("project_name")
    wind_power_curve_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"wind_power_curve_type_{i+1}.csv"
    if len(st.session_state.wind_power_curve_uploaded) < st.session_state.num_wind_types:
        st.session_state.wind_power_curve_uploaded.extend([False] * (st.session_state.num_wind_types - len(st.session_state.wind_power_curve_uploaded)))
    if st.session_state.wind_power_curve_uploaded[i]:
        # Load the uploaded CSV file into a DataFrame
        df = pd.read_csv(wind_power_curve_path)
    else:
        selected_upload_type = st.selectbox(
            f"Select the way to upload the power curve", 
            ['Enter manually', 'Upload a CSV file'])
        if selected_upload_type == 'Enter manually':
        # If no file is uploaded, create a default DataFrame
            df = pd.DataFrame({
                'Wind Speed [m/s]': [],
                'Power [W]': []
            })
        elif selected_upload_type == 'Upload a CSV file':
            uploaded_file, delimiter, decimal = csv_upload_interface(f"power_curve_{i}")
            if uploaded_file:
                data_dict = {}
                wind_speed_power_curve = load_csv_data(uploaded_file, delimiter, decimal, f'Wind Speed [m/s]')
                power_power_curve = load_csv_data(uploaded_file, delimiter, decimal, f'Power [W]')
                data_dict[f'Wind Speed [m/s]'] = wind_speed_power_curve.values.flatten() if wind_speed_power_curve is not None else None
                data_dict[f'Power [W]'] = power_power_curve.values.flatten() if power_power_curve is not None else None
                df = pd.DataFrame(data_dict)
        if st.session_state.wind_power_curve_uploaded[i] or selected_upload_type == 'Enter manually' or uploaded_file:
            # Display the table for editing
            edited_table = st.data_editor(
                df,
                num_rows="dynamic",  # Allows adding/removing rows
                use_container_width=True,
                key="csv_table_editor"
            )

    if st.button("Close"):
        # Store the combined data in session state
        st.session_state.wind_power_curve_uploaded[i] = True  # Set the flag to True since data is now uploaded
        sorted_table = edited_table.sort_values(by='Wind Speed [m/s]')
        sorted_table.to_csv(wind_power_curve_path, index=False)
        st.rerun()

def render_timezone_selector() -> str:
    # List of all available time zones with country names
    timezones_with_countries = ["Universal Time Coordinated - UTC"]  # Manually add UTC at the beginning
    for country_code, timezones in pytz.country_timezones.items():
        country_name = pytz.country_names[country_code]
        for timezone in timezones:
            timezones_with_countries.append(f"{country_name} - {timezone}")

    # Select time zone from a comprehensive list with country names
    selected_timezone_with_country = st.selectbox("Select the time zone for the installation dates:", timezones_with_countries)

    # Extract just the timezone (without the country name)
    selected_timezone = selected_timezone_with_country.split(' - ')[1]

    return selected_timezone

# Function to convert installation dates to UTC
def convert_dates_to_utc(installation_dates: list, timezone_str: str) -> list:
    # Load the timezone
    local_tz = pytz.timezone(timezone_str)

    # Convert each date to UTC
    installation_dates_utc = []
    for date in installation_dates:
        if isinstance(date, dt.datetime):
            # Localize the date to the selected timezone and convert to UTC
            localized_date = local_tz.localize(date)
            utc_date = localized_date.astimezone(pytz.UTC).replace(tzinfo=None)
            installation_dates_utc.append(utc_date)
        else:
            installation_dates_utc.append(None)  # Handle cases where date is not provided

    return installation_dates_utc

def combine_date_and_time(date_value: dt.date, time_value: dt.time) -> dt.datetime:
    """Combine date and time into a datetime object."""
    return dt.datetime.combine(date_value, time_value)

def wind() -> None:
    """Streamlit page for configuring renewable energy technology parameters."""
    st.title("Wind Energy")
    st.subheader("Define the parameters for the Wind Energy")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'wind_parameters')
    st.session_state.wind_num_units = st.number_input("Enter the number of Wind Energy units", min_value=1, value=st.session_state.wind_num_units)
    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.wind_installation_dates) != st.session_state.wind_num_units:
        st.session_state.wind_installation_dates = [dt.datetime.now() for _ in range(st.session_state.wind_num_units)]

    with st.expander(f"Installation Dates", expanded=False):
        st.session_state.selected_timezone_wind = render_timezone_selector()
        if st.session_state.wind_num_units > 1:
            # Checkbox to determine if the installation date is the same for all units
            st.session_state.wind_same_date = st.checkbox("Same installation date for all units", value=st.session_state.wind_same_date)

            if st.session_state.wind_same_date:
                if 'installation_dates' not in st.session_state or len(st.session_state.wind_installation_dates) != st.session_state.wind_num_units:
                    # Initialize with today's date at 00:00
                    today_midnight = dt.datetime.combine(dt.date.today(), dt.time.min)  # Today's date at 00:00
                    st.session_state.wind_installation_dates = [today_midnight for _ in range(st.session_state.wind_num_units)]

                # Single date and time input for all units
                col1, col2 = st.columns(2)
                with col1:
                    same_installation_date = st.date_input(
                        "Installation Date",
                        value=st.session_state.wind_installation_dates[0].date() if st.session_state.wind_installation_dates[0] else dt.datetime.combine(dt.date.today(), dt.time.min)
                    )
                with col2:
                    same_installation_time = st.time_input(
                        "Installation Time",
                        value=st.session_state.wind_installation_dates[0].time() #if st.session_state.installation_dates[0] else dt.datetime.now().time()
                    )
                
                # Combine date and time
                same_installation_datetime = combine_date_and_time(same_installation_date, same_installation_time)
                
                # Set the same datetime for all units
                for i in range(st.session_state.wind_num_units):
                    st.session_state.wind_installation_dates[i] = same_installation_datetime
            else:
                # Multiple date inputs for each unit                
                for i in range(st.session_state.wind_num_units):
                # Create a date and time input for each unit
                    col1, col2 = st.columns(2)
                    with col1:
                        input_date = st.date_input(
                            f"Installation Date for Unit {i + 1}",
                            value=st.session_state.wind_installation_dates[i].date() if st.session_state.wind_installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min),
                            key=f"date_input_{i}"
                        )
                    with col2:
                        input_time = st.time_input(
                            f"Installation Time for Unit {i + 1}",
                            value=st.session_state.wind_installation_dates[i].time() if st.session_state.wind_installation_dates else dt.time.min,
                            key=f"time_input_{i}"
                        )
                    
                    # Combine date and time into a datetime object
                    st.session_state.wind_installation_dates[i] = combine_date_and_time(input_date, input_time)
        else:
            # Only one unit, so no checkbox needed
            st.write("Enter the installation date for the unit:")
            col1, col2 = st.columns(2)
            with col1:
                input_date = st.date_input(
                    "Installation Date",
                    value=st.session_state.wind_installation_dates[0].date() if st.session_state.wind_installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min)
                )
            with col2:
                input_time = st.time_input(
                    "Installation Time",
                    value=st.session_state.wind_installation_dates[0].time() if st.session_state.wind_installation_dates else dt.time.min
                )
            
            # Combine date and time into a datetime object
            st.session_state.wind_installation_dates[0] = combine_date_and_time(input_date, input_time)
        
        st.session_state.wind_installation_dates_utc = convert_dates_to_utc(st.session_state.wind_installation_dates, st.session_state.selected_timezone_wind)

    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.wind_type) != st.session_state.wind_num_units:
        st.session_state.wind_type = [None] * st.session_state.wind_num_units

    if st.session_state.wind_num_units > 1:
        st.write("Enter the number of PV types that were used:")
        # Checkbox to determine if the type is the same for all units
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.wind_same_type = st.checkbox("Same type for all units", value=st.session_state.wind_same_type)

        if st.session_state.wind_same_type:
            # Select the same type for all units
            st.session_state.num_wind_types = 1
            st.session_state.wind_types = ['Type 1']  
            for i in range(st.session_state.wind_num_units):
                st.session_state.wind_type[i] = st.session_state.wind_types[0]
        else:
            with col2:
                st.session_state.num_wind_types = st.number_input("Enter the number of types", min_value=2, max_value=st.session_state.wind_num_units, value=max(st.session_state.num_wind_types,2))
            st.session_state.wind_types = [None] * st.session_state.num_wind_types
            for i in range(st.session_state.num_wind_types):
                st.session_state.wind_types[i] = f'Type {i+1}'

            # Multiple select boxes for each unit
            col1, col2 = st.columns(2)
            for i in range(st.session_state.wind_num_units):
                col = col1 if i % 2 == 0 else col2
                with col:
                    # Create a dropdown to select type for each unit
                    selected_value = st.session_state.wind_type[i] if st.session_state.wind_type[i] else st.session_state.wind_types[0]
                    selected_index = st.session_state.wind_types.index(selected_value)
                    st.session_state.wind_type[i] = st.selectbox(
                        f"Type for Unit {i + 1}",
                        st.session_state.wind_types,
                        index=selected_index,
                        key=f"type_select_{i}"
                    )
    else:
        # If there's only one unit, default to selecting a type for that unit
        st.session_state.num_wind_types = 1
        st.session_state.wind_types = ['Type 1']        
        st.session_state.wind_type[0] = st.session_state.wind_types[0]

    st.session_state.wind_temporal_degradation = st.checkbox("Temporal wind turbine degradation", value=st.session_state.wind_temporal_degradation)

    st.write("Enter the specifications for each wind turbine type:")
    col1, col2 = st.columns(2)
    for i in range(st.session_state.num_wind_types):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(f"Enter Wind Specifications for Type {i+1}"):
                enter_specifications(i)