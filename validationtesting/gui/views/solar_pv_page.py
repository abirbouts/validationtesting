"""
This file contains the code for the Solar PV page of the GUI.
The user can specify the specifications for the solar PV system.
"""

import streamlit as st
from validationtesting.gui.views.utils import initialize_session_state, combine_date_and_time
import datetime as dt

@st.dialog("Enter Solar PV Specifications")
def enter_specifications(i: int) -> None:
    """
    Displays input fields for entering solar PV specifications for a given solar PV type.
    This function dynamically generates input fields for various solar PV specifications based on the
    current state of the application. It handles both technical and economic validation scenarios.
    """
    st.write(f"Enter Solar PV Specifications for Type {i+1}.")

    # Lifetime
    if len(st.session_state.pv_lifetime) != st.session_state.num_solar_pv_types:
        st.session_state.pv_lifetime = [0] * st.session_state.num_solar_pv_types
    st.session_state.pv_lifetime[i] = st.number_input(
        f"Type {i+1} PV lifetime [years]:", 
        min_value=0, 
        value=st.session_state.pv_lifetime[i])

    # Input technical specifications
    if st.session_state.technical_validation:
        # Solar PV calculation type
        st.session_state.solar_pv_calculation_type[i] = st.selectbox(
            f"Using what was the Solar PV energy calculated?",
            ['Area and Efficiency', 'Nominal Power'],
            index=['Area and Efficiency', 'Nominal Power'].index(st.session_state.solar_pv_calculation_type[i]),
            key=f"calculation_type_select_{i}"
        )

        if st.session_state.solar_pv_calculation_type[i] == 'Area and Efficiency':
            # Solar PV area
            if len(st.session_state.pv_area) != st.session_state.num_solar_pv_types:
                st.session_state.pv_area = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_area[i] = st.number_input(
                f"Type {i+1} PV area [m^2]:", 
                min_value=0.0, 
                value=st.session_state.pv_area[i])

            # Solar PV efficiency
            if len(st.session_state.pv_efficiency) != st.session_state.num_solar_pv_types:
                st.session_state.pv_efficiency = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_efficiency[i] = st.number_input(
                f"Type {i+1} PV efficiency [%]:", 
                min_value=0.0, 
                value=st.session_state.pv_efficiency[i])
        
        elif st.session_state.solar_pv_calculation_type[i] == 'Nominal Power':
            # Solar PV nominal power
            if len(st.session_state.pv_nominal_power) != st.session_state.num_solar_pv_types:
                st.session_state.pv_nominal_power = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_nominal_power[i] = st.number_input(
                f"Type {i+1} PV nominal power [W]:", 
                min_value=0.0, 
                value=st.session_state.pv_nominal_power[i])

        # Solar PV tilt angle
        if len(st.session_state.pv_theta_tilt) != st.session_state.num_solar_pv_types:
            st.session_state.pv_theta_tilt = [0.0] * st.session_state.num_solar_pv_types
        st.session_state.pv_theta_tilt[i] = st.number_input(
            f"Type {i+1} PV tilt angle [°]:", 
            min_value=0.0, 
            value=st.session_state.pv_theta_tilt[i])

        # Solar PV azimuth angle
        if len(st.session_state.pv_azimuth) != st.session_state.num_solar_pv_types:
            st.session_state.pv_azimuth = [0.0] * st.session_state.num_solar_pv_types
        st.session_state.pv_azimuth[i] = st.number_input(
            f"Type {i+1} PV azimuth angle [°]:", 
            min_value=-180.0,
            max_value=180.0,
            value=st.session_state.pv_azimuth[i])

        # Solar PV degradation
        if st.session_state.pv_degradation:
            if len(st.session_state.pv_degradation_rate) != st.session_state.num_solar_pv_types:
                st.session_state.pv_degradation_rate = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_degradation_rate[i] = st.number_input(
                f"Type {i+1} PV degradation rate [% per year]:", 
                min_value=0.0, 
                value=st.session_state.pv_degradation_rate[i])
        
        # Solar PV temperature dependent efficiency
        if st.session_state.pv_temperature_dependent_efficiency:
            if len(st.session_state.pv_temperature_coefficient) != st.session_state.num_solar_pv_types:
                st.session_state.pv_temperature_coefficient = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_temperature_coefficient[i] = st.number_input(
                f"Type {i+1} PV temperature coefficient [% per °C]:", 
                value=st.session_state.pv_temperature_coefficient[i])
            
            if len(st.session_state.pv_T_ref) != st.session_state.num_solar_pv_types:
                st.session_state.pv_T_ref = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_T_ref[i] = st.number_input(
                f"Type {i+1} PV refrence Temperature [°C]:", 
                min_value=0.0, 
                value=st.session_state.pv_T_ref[i])
            
            if len(st.session_state.pv_T_ref_NOCT) != st.session_state.num_solar_pv_types:
                st.session_state.pv_T_ref_NOCT = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_T_ref_NOCT[i] = st.number_input(
                f"Type {i+1} PV NOCT reference temperature [°C]:", 
                min_value=0.0, 
                value=st.session_state.pv_T_ref_NOCT[i])
            
            if len(st.session_state.pv_NOCT) != st.session_state.num_solar_pv_types:
                st.session_state.pv_NOCT = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_NOCT[i] = st.number_input(
                f"Type {i+1} PV NOCT [°C]:", 
                min_value=0.0, 
                value=st.session_state.pv_NOCT[i])
            
            if len(st.session_state.pv_I_ref_NOCT) != st.session_state.num_solar_pv_types:
                st.session_state.pv_I_ref_NOCT = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_I_ref_NOCT[i] = st.number_input(
                f"Type {i+1} PV NOCT reference irradiation [Wh/m^2]:", 
                min_value=0.0, 
                value=st.session_state.pv_I_ref_NOCT[i])
        
        # Solar PV dynamic inverter efficiency
        if not st.session_state.pv_dynamic_inverter_efficiency:
            if len(st.session_state.pv_inverter_efficiency) != st.session_state.num_solar_pv_types:
                st.session_state.pv_inverter_efficiency = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_inverter_efficiency[i] = st.number_input(
                f"Type {i+1} inverter efficiency [%]:", 
                min_value=0.0, 
                value=st.session_state.pv_inverter_efficiency[i])

    # Input economic specifications    
    if st.session_state.economic_validation:
        # Investment Cost
        col1, col2 = st.columns(2)
        with col1:
            if len(st.session_state.solar_pv_investment_cost) != st.session_state.num_solar_pv_types:
                st.session_state.solar_pv_investment_cost = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.solar_pv_investment_cost[i] = st.number_input(
                f"Investment Cost []:", 
                min_value=0.0, 
                value=st.session_state.solar_pv_investment_cost[i],
                key=f"solar_pv_investment_cost_{i}"
            )
        with col2:
            if len(st.session_state.solar_pv_exclude_investment_cost) != st.session_state.num_solar_pv_types:
                st.session_state.solar_pv_exclude_investment_cost = [False] * st.session_state.num_solar_pv_types
            st.session_state.solar_pv_exclude_investment_cost[i] = st.checkbox(
                "Exclude Investment Cost", 
                value = st.session_state.solar_pv_exclude_investment_cost[i])

        # Yearly Operation and Maintenance Cost
        if len(st.session_state.solar_pv_maintenance_cost) != st.session_state.num_solar_pv_types:
            st.session_state.solar_pv_maintenance_cost = [0.0] * st.session_state.num_solar_pv_types
        st.session_state.solar_pv_maintenance_cost[i] = st.number_input(
            f"Yearly Operation and Maintenance Cost [% of investment cost per year]:", 
            min_value=0.0, 
            value=st.session_state.solar_pv_maintenance_cost[i],
            key=f"solar_pv_maintenance_cost_{i}"
        )

        # End of Project Cost
        if len(st.session_state.solar_pv_end_of_project_cost) != st.session_state.num_solar_pv_types:
            st.session_state.solar_pv_end_of_project_cost = [0.0] * st.session_state.num_solar_pv_types
        st.session_state.solar_pv_end_of_project_cost[i] = st.number_input(
            f"End of Project Cost []:", 
            min_value=0.0, 
            value=st.session_state.solar_pv_end_of_project_cost[i],
            key=f"solar_pv_end_of_project_cost_{i}"
        )


    if st.button("Close"):
        st.rerun()


def solar_pv() -> None:
    """
    Streamlit page for configuring solar PV technology parameters.
    """
    st.title("Solar PV")
    st.subheader("Define the parameters for Solar PV")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'solar_pv_parameters')
    st.session_state.solar_pv_num_units = st.number_input("Enter the number of units", min_value=1, value=st.session_state.solar_pv_num_units)
    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.installation_dates) != st.session_state.solar_pv_num_units:
        st.session_state.installation_dates = [dt.datetime.now() for _ in range(st.session_state.solar_pv_num_units)]

    with st.expander(f"Installation Dates", expanded=False):
        if st.session_state.solar_pv_num_units > 1:
            # Checkbox to determine if the installation date is the same for all units
            st.session_state.same_date = st.checkbox("Same installation date for all units", value=st.session_state.same_date)
            if st.session_state.same_date:
                if 'installation_dates' not in st.session_state or len(st.session_state.installation_dates) != st.session_state.solar_pv_num_units:
                    # Initialize with today's date at 00:00
                    today_midnight = dt.datetime.combine(dt.date.today(), dt.time.min)  # Today's date at 00:00
                    st.session_state.installation_dates = [today_midnight for _ in range(st.session_state.solar_pv_num_units)]

                # Single date and time input for all units
                same_installation_date = st.date_input(
                    "Installation Date",
                    value=st.session_state.installation_dates[0].date() if st.session_state.installation_dates[0] else dt.datetime.combine(dt.date.today(), dt.time.min)
                )

                # Combine date and time
                same_installation_datetime = combine_date_and_time(same_installation_date)
                
                # Set the same datetime for all units
                for i in range(st.session_state.solar_pv_num_units):
                    st.session_state.installation_dates[i] = same_installation_datetime
            else:
                # Multiple date inputs for each unit
                st.write("Enter the installation date for each unit:")
                
                for i in range(st.session_state.solar_pv_num_units):
                # Create a date and time input for each unit
                    input_date = st.date_input(
                        f"Installation Date for Unit {i + 1}",
                        value=st.session_state.installation_dates[i].date() if st.session_state.installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min),
                        key=f"date_input_{i}"
                    )
                    
                    # Combine date and time into a datetime object
                    st.session_state.installation_dates[i] = combine_date_and_time(input_date)
        else:
            # Only one unit, so no checkbox needed
            st.write("Enter the installation date for the unit:")
            input_date = st.date_input(
                "Installation Date",
                value=st.session_state.installation_dates[0].date() if st.session_state.installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min)
            )
            
            # Combine date and time into a datetime object
            st.session_state.installation_dates[0] = combine_date_and_time(input_date)
        
    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.solar_pv_type) != st.session_state.solar_pv_num_units:
        st.session_state.solar_pv_type = [None] * st.session_state.solar_pv_num_units

    if st.session_state.solar_pv_num_units > 1:
        st.write("Enter the number of PV types that were used:")
        col1, col2 = st.columns(2)
        # Checkbox to determine if the type is the same for all units
        with col1:
            st.session_state.same_type = st.checkbox("Same type for all units", value=st.session_state.same_type)

        if st.session_state.same_type:
            # Select the same type for all units
            st.session_state.num_solar_pv_types = 1
            st.session_state.solar_pv_types = ['Type 1']  
            for i in range(st.session_state.solar_pv_num_units):
                st.session_state.solar_pv_type[i] = st.session_state.solar_pv_types[0]
        else:
            with col2:
                st.session_state.num_solar_pv_types = st.number_input("Enter the number of types", min_value=2, max_value=st.session_state.solar_pv_num_units, value=max(st.session_state.num_solar_pv_types,2))
            st.session_state.solar_pv_types = [None] * st.session_state.num_solar_pv_types
            for i in range(st.session_state.num_solar_pv_types):
                st.session_state.solar_pv_types[i] = f'Type {i+1}'

            # Multiple select boxes for each unit
            col1, col2 = st.columns(2)
            for i in range(st.session_state.solar_pv_num_units):
                col = col1 if i % 2 == 0 else col2
                with col:
                    # Create a dropdown to select type for each unit
                    selected_value = st.session_state.solar_pv_type[i] if st.session_state.solar_pv_type[i] else st.session_state.solar_pv_types[0]
                    selected_index = st.session_state.solar_pv_types.index(selected_value)
                    st.session_state.solar_pv_type[i] = st.selectbox(
                        f"Type for Unit {i + 1}",
                        st.session_state.solar_pv_types,
                        index=selected_index,
                        key=f"type_select_{i}"
                    )
    else:
        # If there's only one unit, default to selecting a type for that unit
        st.session_state.num_solar_pv_types = 1
        st.session_state.solar_pv_types = ['Type 1']        
        st.session_state.solar_pv_type[0] = st.session_state.solar_pv_types[0]

    # Define what should be included in the calculations
    if st.session_state.technical_validation:
        st.write("Choose what was included in your calculations:")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.pv_degradation = st.checkbox("Yearly PV degradation", value=st.session_state.pv_degradation)
        with col2:
            st.session_state.pv_temperature_dependent_efficiency = st.checkbox("Temperature dependent PV efficiency", value=st.session_state.pv_temperature_dependent_efficiency)


        st.session_state.pv_rho = st.number_input(
            f"Ground reflectance (rho) [%]:", 
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.pv_rho)

    # Display the input fields for each type
    st.write("Enter the specifications for each type of solar PV:")
    col1, col2 = st.columns(2)
    for i in range(st.session_state.num_solar_pv_types):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(f"Enter Solar PV Specifications for Type {i+1}"):
                enter_specifications(i)