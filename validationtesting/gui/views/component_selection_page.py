import streamlit as st
import pandas as pd
from validationtesting.gui.views.utils import initialize_session_state

def component_selection():
    """Streamlit page for configuring advanced settings."""
    # Page title and description
    st.title("Component Selection")
    st.write("Select components that should be included in the validtation test.")

    initialize_session_state(st.session_state.default_values, 'component_selection')
    
    st.session_state.solar_pv = st.toggle("☀️Solar Photovoltaics", value=st.session_state.solar_pv)
    st.session_state.wind = st.toggle("🌀Wind Energy", value=st.session_state.wind)
    st.session_state.generator = st.toggle("⚙️Generator", value=st.session_state.generator)
    st.session_state.battery = st.toggle("🔋Battery", value=st.session_state.battery)
