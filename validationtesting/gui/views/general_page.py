"""
This script defines a Streamlit page for configuring general project information, including location selection.
It includes functions to get coordinates from an address, handle location input by clicking on a map, and render the main page with 
options to select the project location either by entering an address, clicking on a map or inputting coordinates.
"""


import streamlit as st
import folium
import datetime as dt
from validationtesting.gui.views.utils import initialize_session_state, timezone_selector, generate_flow_chart
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
from typing import Tuple

def get_coordinates(address: str) -> Tuple[float, float]:
    """Get the latitude and longitude coordinates for the given address."""
    geolocator = Nominatim(user_agent="myGeocoder")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return location.latitude, location.longitude
        raise ValueError(f"No location found for the given address: {address}")
    except GeopyError as e:
        raise ValueError(f"Geocoding error: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {e}")

def handle_location_input(address: str) -> None:
    """Handle the input address to get the coordinates and update the session state."""
    try:
        lat, lon = get_coordinates(address)
        st.session_state.lat = lat
        st.session_state.lon = lon
        st.session_state.location = f"{lat}, {lon}"
        st.success("Location found!")
    except ValueError as e:
        st.error(f"Could not find location: {e}")

def general() -> None:
    """Streamlit page for configuring general settings."""
    # Page title and description
    st.title("General Project Information")

    initialize_session_state(st.session_state.default_values, 'general_info')

    # Define start and end date for the project
    start_date = st.date_input("Start Date", 
                               value=st.session_state.start_date.date())
    st.session_state.start_date = dt.datetime.combine(start_date, dt.time.min)
    
    end_date = st.date_input("End Date", 
                             value=st.session_state.end_date)
    st.session_state.end_date = dt.datetime.combine(end_date, dt.time(23, 0))
    
    timezone_selector()

    # Define discount rate
    if st.session_state.economic_validation:
        st.session_state.discount_rate = st.number_input("Discount Rate (%)", 
                                                        value=st.session_state.discount_rate, 
                                                        format="%.2f")

    # Define project location   
    if st.session_state.technical_validation:
        if st.session_state.solar_pv or st.session_state.wind:
            # Location selection
            st.subheader("Select Project Location")

            # Dropdown for selecting the method of input
            location_input_method = st.selectbox(
                "Choose how to input location:",
                ("Select on Map", "Enter Coordinates Manually")
            )

            if location_input_method == "Select on Map":
                # Address input field
                address = st.text_input("Enter location address:", 
                                        help="Input a specific address or location name to set project coordinates.")
                
                # Handle address input to get coordinates (you need to implement handle_location_input)
                if address:
                    handle_location_input(address)

                # Initialize the map with the current coordinates
                initial_coords = [st.session_state.lat, st.session_state.lon]
                m = folium.Map(location=initial_coords, zoom_start=5)
                folium.Marker(initial_coords, tooltip="Project Location").add_to(m)

                # Display the map
                output = st_folium(m, width=700, height=500)

                # Update coordinates based on the last clicked point on the map
                if output and output.get('last_clicked'):
                    st.session_state.lat = output['last_clicked']['lat']
                    lon = output['last_clicked']['lng']
                    lon = lon % 360
                    if lon > 180:
                        lon = lon - 360
                    if lon < -180:
                        lon = lon + 360
                    st.session_state.lon = lon

            elif location_input_method == "Enter Coordinates Manually":
                # Manually input latitude and longitude
                st.session_state.lat = st.number_input("Enter Latitude:", value=st.session_state.lat, format="%.6f")
                st.session_state.lon = st.number_input("Enter Longitude:", value=st.session_state.lon, format="%.6f")

            st.write(f"Selected Coordinates: {st.session_state.lat}, {st.session_state.lon}")
