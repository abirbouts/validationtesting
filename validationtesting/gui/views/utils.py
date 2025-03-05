"""
This module provides utility functions for rendering the footer in the MicroGridsPy Streamlit application.
It includes functions to convert images to base64 strings and to render a footer with links to documentation, GitHub, and contact email.
It also includes functions to initialize session state variables, create an interface for CSV file upload, and select time formats and time zones.
"""

import base64
import streamlit as st
import pytz
import re
import datetime as dt
import pandas as pd

from typing import Tuple, Any
from io import BytesIO
from pathlib import Path
from PIL import Image

from config.path_manager import PathManager



def get_base64_image(image_path: Path, width: int, height: int) -> str:
    """Convert image to base64 string after resizing."""
    img = Image.open(image_path)
    img = img.resize((width, height), Image.LANCZOS)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def render_footer() -> None:
    """Render the footer with icons linking to documentation, GitHub, and contact email."""
    doc_icon_base64 = get_base64_image(PathManager.ICONS_PATH / "doc_icon.ico", 20, 20)
    github_icon_base64 = get_base64_image(PathManager.ICONS_PATH / "github_icon.ico", 20, 20)
    mail_icon_base64 = get_base64_image(PathManager.ICONS_PATH / "mail_icon.ico", 20, 20)

    st.markdown(
        f"""
        <div class="footer">
            <div class="footer-right">
                <a href="{PathManager.DOCS_URL}" target="_blank">
                    <img src="{doc_icon_base64}" alt="Documentation" class="footer-icon">
                </a>
                <a href="{PathManager.GITHUB_URL}" target="_blank">
                    <img src="{github_icon_base64}" alt="GitHub" class="footer-icon">
                </a>
                <a href="mailto:{PathManager.MAIL_CONTACT}">
                    <img src="{mail_icon_base64}" alt="Contact" class="footer-icon">
                </a>
            </div>
        </div>
        <style>
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #d8d8d8;
            text-align: center;
            padding: 10px;
        }}

        .footer-right {{
            float: right;
        }}
        </style>
        """,
        unsafe_allow_html=True)
    
def render_top_left_icons() -> None:
    """Render icons on the top-left corner with links to documentation and GitHub."""
    doc_icon_base64 = get_base64_image(PathManager.ICONS_PATH / "doc_icon.ico", 20, 20)
    github_icon_base64 = get_base64_image(PathManager.ICONS_PATH / "github_icon.ico", 20, 20)
    github_icon_base64 = get_base64_image(PathManager.ICONS_PATH / "eth.png", 20, 20)

    st.markdown(
        f"""
        <div class="top-left-icons">
            <a href="{PathManager.DOCS_URL}" target="_blank">
                <img src="{doc_icon_base64}" alt="Documentation" class="top-icon">
            </a>
            <a href="{PathManager.GITHUB_URL}" target="_blank">
                <img src="{github_icon_base64}" alt="GitHub" class="top-icon">
            </a>
        </div>
        <style>
        .top-left-icons {{
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 100;
            display: flex;
            align-items: center;
        }}

        .top-icon {{
            margin-right: 10px;
            height: 20px;
            width: 20px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def initialize_session_state(default_values: Any, settings_type: str) -> None:
    """Initialize session state variables from default values."""
    for key, value in vars(getattr(default_values, settings_type)).items():
        if key not in st.session_state:
            st.session_state[key] = value


def csv_upload_interface(key_prefix: str) -> Tuple[st.file_uploader, str, str]:
    """
    Create an interface for CSV file upload with delimiter and decimal selection.
    
    Args:
        key_prefix (str): A prefix for Streamlit widget keys to avoid conflicts.
    
    Returns:
        Tuple[st.file_uploader, str, str]: Uploaded file, selected delimiter, and decimal separator.
    """
    delimiter_options = {
        "Comma (,)": ",",
        "Semicolon (;)": ";",
        "Tab (\\t)": "\t"}
    
    decimal_options = {
        "Dot (.)": ".",
        "Comma (,)": ","}
    
    delimiter = st.selectbox("Select delimiter", list(delimiter_options.keys()), key=f"{key_prefix}_delimiter")
    decimal = st.selectbox("Select decimal separator", list(decimal_options.keys()), key=f"{key_prefix}_decimal")
    
    delimiter_value = delimiter_options[delimiter]
    decimal_value = decimal_options[decimal]
    
    uploaded_file = st.file_uploader(f"Choose a CSV file", type=["csv"], key=f"{key_prefix}_uploader")
    
    return uploaded_file, delimiter_value, decimal_value

def time_format_selectors() -> tuple:
    """
    Create selectors for time format and time zone.
    """
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
    st.write(f"Selected Time Format: {time_format}")


    return time_format

def timezone_selector() -> tuple:
    """
    Create a selector for time zone.
    """
    current_time_zone = st.session_state.timezone

    # If the current timezone is in the Etc/GMT format, convert it to the corresponding UTC offset string.
    if current_time_zone and "Etc/GMT" in current_time_zone:
        match = re.search(r'Etc/GMT([+-]\d+)', current_time_zone)
        if match:
            offset = int(match.group(1))
            utc_offset = -offset
            sign = "+" if utc_offset >= 0 else "-"
            hours = abs(utc_offset)
            current_time_zone = f"UTC Offset {sign}{hours:02d}:00"

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

    # Select time zone from a comprehensive list with country names
    selected_timezone_with_country = st.selectbox("Select the time zone for the project:", 
                                                  timezones_with_countries,
                                                  index=timezones_with_countries.index(current_time_zone) if current_time_zone in timezones_with_countries else 0)

    if "UTC Offset" in selected_timezone_with_country:
        match = re.search(r'[+-]\d+', selected_timezone_with_country)
        offset = int(match.group())
        offset = offset * (-1)
        selected_timezone = f"Etc/GMT{'+' if offset > 0 else ''}{offset}"
    else:
        # Extract just the timezone (without the country name)
        selected_timezone = selected_timezone_with_country.split(' - ')[1]
    
    st.session_state.timezone = selected_timezone
    
    return

def convert_dates_to_utc(dates: list[dt.datetime], timezone_str: str) -> list[dt.datetime]:
    """
    Convert a list of dates to UTC using the provided timezone.
    """
    # Load the timezone
    local_tz = pytz.timezone(timezone_str)

    # Convert each date to UTC
    dates_utc = []
    for date in dates:
        if isinstance(date, dt.datetime):
            # Localize the date to the selected timezone and convert to UTC
            localized_date = local_tz.localize(date)
            utc_date = localized_date.astimezone(pytz.UTC).replace(tzinfo=None)
            dates_utc.append(utc_date)
        else:
            dates_utc.append(None)  # Handle cases where date is not provided

    return dates_utc

def combine_date_and_time(date_value: dt.date) -> dt.datetime:
    """Combine date and time into a datetime object."""
    return dt.datetime.combine(date_value, dt.time(0, 0))

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
    

# Function to load and process time series data with time zones and format handling
def load_timeseries_csv(uploaded_file, delimiter: str, decimal: str, time_format: str) -> pd.DataFrame:
    """
    Load CSV time-series data with given delimiter, decimal options, and convert the time column to UTC datetime.
    
    Args:
        uploaded_file: The uploaded CSV file.
        delimiter (str): The delimiter used in the CSV file.
        decimal (str): The decimal separator used in the CSV file.
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
        
        time = data[time_column]

        if time.empty:
            st.warning("No valid time series data found. Please check the CSV file.")
        else:
            st.success(f"Time loaded successfully for Time and converted to UTC.")

        return time
    
    except Exception as e:
        st.error(f"Error during import of time from CSV: {e}")
        return None
    
def generate_flow_chart() -> None:
    has_solar = st.session_state.solar_pv
    has_wind = st.session_state.wind
    has_battery = st.session_state.battery
    has_generator = st.session_state.generator

    mermaid_code = "flowchart TB\n"
    if st.session_state.current_type == "Alternating Current":
        if has_solar and st.session_state.solar_pv_connection_type == "Connected with the same Inverter as the Battery to the Microgrid":
            mermaid_code += "subgraph Shared_System [DC Subystem]\n"
            mermaid_code += f"Solar_PV --> DC_System\n"
            mermaid_code += "Battery <--> DC_System\n"
            mermaid_code += "DC_System <--> Inverter_DC_System\n"
            mermaid_code += "end\n"
            mermaid_code += "Inverter_DC_System <--> Microgrid\n"
            if has_wind:
                if st.session_state.wind_connection_type == "Connected with a AC-AC Converter to the Microgrid":
                    mermaid_code += f"Wind --> AC-AC_Converter_Wind\n"
                    mermaid_code += f"AC-AC_Converter_Wind --> Microgrid\n"
                else:
                    mermaid_code += f"Wind --> Microgrid\n"
            if has_generator:
                mermaid_code += "Generator --> Microgrid\n"

        else:
            if has_solar and st.session_state.solar_pv_connection_type == "Connected with a seperate Inverter to the Microgrid":
                    mermaid_code += f"Solar_PV --> Inverter_Solar_PV\n"
                    mermaid_code += f"Inverter_Solar_PV --> Microgrid\n"
            if has_wind:
                if st.session_state.wind_connection_type == "Connected with a AC-AC Converter to the Microgrid":
                    mermaid_code += f"Wind --> AC-AC_Converter_Wind\n"
                    mermaid_code += f"AC-AC_Converter_Wind --> Microgrid\n"
                else:
                    mermaid_code += f"Wind --> Microgrid\n"
            if has_battery:
                mermaid_code += "Battery <--> Inverter_Battery\n"
                mermaid_code += "Inverter_Battery <--> Microgrid\n"
            if has_generator:
                mermaid_code += "Generator --> Microgrid\n"
    
    else:
        if has_solar:
            mermaid_code += f"Solar_PV --> Microgrid\n"
        if has_wind:
            mermaid_code += f"Wind --> Rectifier_Wind\n"
            mermaid_code += f"Rectifier_Wind --> Microgrid\n"
        if has_battery:
            mermaid_code += "Battery <--> Microgrid\n"
        if has_generator:
            mermaid_code += "Generator --> Rectifier_Generator\n"
            mermaid_code += "Rectifier_Generator --> Microgrid\n"

    # Add final connection to Load
    mermaid_code += "Microgrid --> Load\n"

    # Wrap Mermaid code in the HTML template
    mermaid_html = f"""
    <div class="mermaid">
    {mermaid_code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
        }});
    </script>
    """

    # Display the generated Mermaid flowchart
    st.components.v1.html(mermaid_html, height=700)