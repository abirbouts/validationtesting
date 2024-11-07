import streamlit as st
import pandas as pd

from validationtesting.gui.views.utils import initialize_session_state

def display_timeline(time_horizon, step_duration):
    """Display project timeline as a table."""
    num_steps = time_horizon // step_duration
    min_step_duration = time_horizon - step_duration * num_steps
    
    step_durations = [step_duration] * num_steps
    if min_step_duration > 0:
        step_durations.append(min_step_duration)
        num_steps += 1

    st.session_state.num_steps = num_steps

    timeline_data = {
        "Step": [f"Investment Step {i + 1}" for i in range(num_steps)],
        "Duration [Years]": step_durations} 
    
    df_timeline = pd.DataFrame(timeline_data)
    st.table(df_timeline)

def component_selection():
    """Streamlit page for configuring advanced settings."""
    # Page title and description
    st.title("Component Selection")
    st.write("Select components that should be included in the validtation test.")

    initialize_session_state(st.session_state.default_values, 'component_selection')

    st.session_state.solar_pv = st.checkbox(
        "Solar Photovoltaics", 
        value=st.session_state.solar_pv)
    st.session_state.wind = st.checkbox(
        "Wind Energy", 
        value=st.session_state.wind)
    st.session_state.generator = st.checkbox(
        "Generator", 
        value=st.session_state.generator)
    st.session_state.battery = st.checkbox(
        "Battery", 
        value=st.session_state.battery)
    

    # Navigation buttons
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("Back"):
            st.session_state.page = "Initial Page"
            st.rerun()
    with col2:
        if st.button("Next"):
            st.session_state.page = "Initial Page"
            st.rerun()