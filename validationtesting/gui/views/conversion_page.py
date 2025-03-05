import streamlit as st
from validationtesting.gui.views.utils import initialize_session_state, generate_flow_chart



def conversion() -> None:

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'conversion_parameters')

    st.subheader("Select System Architecture")
    st.session_state.current_type = st.selectbox("Select System Architecture", ["Alternating Current", "Direct Current"])
    
    if st.session_state.current_type == "Alternating Current":
        if st.session_state.solar_pv:
            if st.session_state.battery:
                options =["Connected with a seperate Inverter to the Microgrid", "Connected with the same Inverter as the Battery to the Microgrid"]
                if st.session_state.solar_pv_connection_type not in options:
                    st.session_state.solar_pv_connection_type = options[1]
                st.session_state.solar_pv_connection_type = st.selectbox(
                        f"Connection to the Microgrid for Solar PV", 
                        options, 
                        index=options.index(st.session_state.solar_pv_connection_type),
                        help="Select the connection type of solar PV. This determines the configuration options and data processing.")
                if st.session_state.solar_pv_connection_type == options[0]:
                    st.session_state.solar_pv_conversion_efficiency = st.number_input(
                        "Inverter Efficiency of Solar PV",
                        value=st.session_state.solar_pv_conversion_efficiency,
                        min_value=0.0,
                        max_value=100.0,
                        step=0.01,
                        help="Enter the efficiency of the inverter for solar PV. This is used to calculate the AC output of the solar PV system.")
                else:
                    st.session_state.solar_pv_conversion_efficiency = 100.0
            else:
                st.session_state.solar_pv_connection_type = "Connected with a seperate Inverter to the Microgrid"
        if st.session_state.wind:
            options = ["Connected directly to the Microgrid", "Connected with a AC-AC Converter to the Microgrid"]
            if st.session_state.wind_connection_type not in options:
                st.session_state.wind_connection_type = options[1]
            st.session_state.wind_connection_type = st.selectbox(
                    f"Connection to the Microgrid for Wind Turbine", 
                    options, 
                    index=options.index(st.session_state.wind_connection_type),
                    help="Select the connection type of wind turbine. This determines the configuration options and data processing.")
            if st.session_state.wind_connection_type == options[1]:
                st.session_state.wind_conversion_efficiency = st.number_input(
                    "Inverter Efficiency of Wind Turbine",
                    value=st.session_state.wind_conversion_efficiency,
                    min_value=0.0,
                    max_value=100.0,
                    step=0.01,
                    help="Enter the efficiency of the conversion for wind turbine. This is used to calculate the AC output of the wind turbine.")
    elif st.session_state.current_type == "Direct Current":
        if st.session_state.solar_pv:
            st.session_state.solar_pv_connection_type = "Connected directly to the Microgrid"
            st.session_state.solar_pv_conversion_efficiency = 100.0
        if st.session_state.wind:
            st.session_state.wind_connection_type = "Connected with a Rectifier to the Microgrid"
            st.session_state.wind_conversion_efficiency = st.number_input(
                "Rectifier Efficiency of Wind Turbine",
                value=st.session_state.wind_conversion_efficiency,
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                help="Enter the efficiency of the rectifier for wind turbine. This is used to calculate the DC output of the wind turbine.")
    if st.session_state.generator:
        if st.session_state.current_type == "Alternating Current":
            st.session_state.generator_conversion_efficiency = 100.0
        elif st.session_state.current_type == "Direct Current":
            st.session_state.generator_conversion_efficiency = st.number_input(
                "Rectifier Efficiency of Generator",
                value=st.session_state.generator_conversion_efficiency,
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                help="Enter the efficiency of the rectifier for generator. This is used to calculate the DC output of the generator.")
    if st.session_state.battery:
        if st.session_state.current_type == "Direct Current":
            st.session_state.battery_conversion_efficiency_ac_dc = 100.0
            st.session_state.battery_conversion_efficiency_dc_ac = 100.0
        elif st.session_state.current_type == "Alternating Current":
            st.session_state.battery_conversion_efficiency_ac_dc = st.number_input(
                "Inverter Efficiency of Battery AC -> DC",
                value=st.session_state.battery_conversion_efficiency_ac_dc,
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                help="Enter the efficiency of the inverter from AC to DC for battery.")
            st.session_state.battery_conversion_efficiency_dc_ac = st.number_input(
                "Inverter Efficiency of Battery DC -> AC",
                value=st.session_state.battery_conversion_efficiency_dc_ac,
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                help="Enter the efficiency of the inverter from DC to AC for battery.")

    generate_flow_chart()
