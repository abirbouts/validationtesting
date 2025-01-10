"""
This script defines a Streamlit page for selecting components to be included in the validation tests.
It includes functions to initialize session state variables and render toggle buttons for various components.
"""

import streamlit as st
from validationtesting.gui.views.utils import initialize_session_state

def component_selection() -> None:
    """Streamlit page for selecting components to be included in the validation tests."""
    st.title("Component Selection")
    st.write("Select components that should be included in the validtation test.")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'component_selection')
    
    col1, col2 = st.columns(2)

    with col1:
        # Toggle buttons for selecting components
        st.session_state.solar_pv = st.toggle("☀️Solar Photovoltaics", value=st.session_state.solar_pv)
        st.session_state.wind = st.toggle("🌀Wind Energy", value=st.session_state.wind)
        st.session_state.generator = st.toggle("⚙️Generator", value=st.session_state.generator)
        st.session_state.battery = st.toggle("🔋Battery", value=st.session_state.battery)
    
    with col2:
        # Toggle buttons for selecting validation types
        st.session_state.technical_validation = st.toggle("⚙️Technical Validation", value=st.session_state.technical_validation)
        st.session_state.economic_validation = st.toggle("💵Economic Validation", value=st.session_state.economic_validation) 
        st.session_state.energy_balance = st.toggle("⚖️Energy Balance", value=st.session_state.energy_balance)