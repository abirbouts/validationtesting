"""
This script defines a Streamlit page for selecting components to be included in the validation tests.
It includes functions to initialize session state variables and render toggle buttons for various components.
Functions:
    component_selection():
        Renders the Streamlit page for component selection, including toggles for all components.
"""

import streamlit as st
import pandas as pd
from validationtesting.gui.views.utils import initialize_session_state

def component_selection() -> None:
    st.title("Component Selection")
    st.write("Select components that should be included in the validtation test.")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'component_selection')
    
    # Toggle buttons for selecting components
    st.session_state.solar_pv = st.toggle("☀️Solar Photovoltaics", value=st.session_state.solar_pv)
    st.session_state.wind = st.toggle("🌀Wind Energy", value=st.session_state.wind)
    st.session_state.generator = st.toggle("⚙️Generator", value=st.session_state.generator)
    st.session_state.battery = st.toggle("🔋Battery", value=st.session_state.battery)
