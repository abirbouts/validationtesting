"""
This module provides utility functions for rendering the footer in the MicroGridsPy Streamlit application.
It includes functions to convert images to base64 strings and to render a footer with links to documentation, GitHub, and contact email.
"""
import base64
import streamlit as st
import pytz
import re

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

def time_format_timezone_selectors() -> tuple:
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

    return time_format, selected_timezone

def timezone_selector() -> tuple:
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
    selected_timezone_with_country = st.selectbox("Select the time zone of the data (with country):", timezones_with_countries)

    if "UTC Offset" in selected_timezone_with_country:
        match = re.search(r'[+-]\d+', selected_timezone_with_country)
        offset = int(match.group())
        offset = offset * (-1)
        selected_timezone = f"Etc/GMT{'+' if offset > 0 else ''}{offset}"
    else:
        # Extract just the timezone (without the country name)
        selected_timezone = selected_timezone_with_country.split(' - ')[1]

    return selected_timezone
