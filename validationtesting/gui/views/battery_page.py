"""
This file contains the code for the Battery page of the GUI.
The user can specify the specifications for the batteries.
"""

import streamlit as st
from validationtesting.gui.views.utils import initialize_session_state, timezone_selector, convert_dates_to_utc, combine_date_and_time
import datetime as dt
import numpy as np

# Function to initialize session state variables (opens dialog box)
@st.dialog("Enter Battery Specifications")
def enter_specifications(i: int) -> None:
    """
    Displays input fields for entering battery specifications for a given battery type.
    This function dynamically generates input fields for various battery specifications based on the 
    current state of the application. It handles both technical and economic validation scenarios.
    """
    st.write(f"Enter Battery Specifications for Type {i+1}.")

    # Battery Lifetime
    if len(st.session_state.battery_lifetime) != st.session_state.num_battery_types:
        st.session_state.battery_lifetime = [0] * st.session_state.num_battery_types
    st.session_state.battery_lifetime[i] = st.number_input(
        f"Battery Lifetime [years]:", 
        min_value=0, 
        value=st.session_state.battery_lifetime[i],
        key=f"battery_lifetime_{i}"
    )

    if st.session_state.technical_validation:
        # Battery Capacity
        if len(st.session_state.battery_capacity) != st.session_state.num_battery_types:
            st.session_state.battery_capacity = [0.0] * st.session_state.num_battery_types
        st.session_state.battery_capacity[i] = st.number_input(
            f"Battery Capacity [Wh]:", 
            min_value=0.0, 
            value=st.session_state.battery_capacity[i],
            key=f"battery_capacity_{i}"
        )

        # Battery Initial State of Charge
        if len(st.session_state.battery_initial_soc) != st.session_state.num_battery_types:
            st.session_state.battery_initial_soc = [0.0] * st.session_state.num_battery_types
        st.session_state.battery_initial_soc[i] = st.number_input(
            f"Initial State of Charge [%]:", 
            min_value=0.0, 
            max_value=100.0, 
            value=st.session_state.battery_initial_soc[i],
            key=f"battery_initial_soc_{i}"
        )

        # Battery Minimum and Maximum State of Charge
        if len(st.session_state.battery_min_soc) != st.session_state.num_battery_types:
            st.session_state.battery_min_soc = [0.0] * st.session_state.num_battery_types
        st.session_state.battery_min_soc[i] = st.number_input(
            f"Minimum State of Charge [%]:", 
            min_value=0.0, 
            max_value=100.0, 
            value=st.session_state.battery_min_soc[i],
            key=f"battery_min_soc_{i}"
        )
        if len(st.session_state.battery_max_soc) != st.session_state.num_battery_types:
            st.session_state.battery_max_soc = [0.0] * st.session_state.num_battery_types
        st.session_state.battery_max_soc[i] = st.number_input(
            f"Maximum State of Charge [%]:", 
            min_value=0.0, 
            max_value=100.0, 
            value=st.session_state.battery_max_soc[i],
            key=f"battery_max_soc_{i}"
        )
        
        # Battery Maximum Charging and Discharging Power
        if len(st.session_state.battery_max_charge_power) < st.session_state.num_battery_types:
            st.session_state.battery_max_charge_power = [0.0] * st.session_state.num_battery_types
        st.session_state.battery_max_charge_power[i] = st.number_input(
            f"Maximum Charging Power [W]:", 
            min_value=0.0, 
            value=st.session_state.battery_max_charge_power[i],
            key=f"battery_max_charge_power_{i}"
        )
        if len(st.session_state.battery_max_discharge_power) != st.session_state.num_battery_types:
            st.session_state.battery_max_discharge_power = [0.0] * st.session_state.num_battery_types
        st.session_state.battery_max_discharge_power[i] = st.number_input(
            f"Maximum Discharging Power [W]:", 
            min_value=0.0, 
            value=st.session_state.battery_max_discharge_power[i],
            key=f"battery_max_discharge_power_{i}"
        )

        # Battery Efficiency (either Seperate Charging and Discharging Efficiency or Roundtrip Efficiency)
        if st.session_state.battery_efficiency_type == 'Seperate Charging and Discharging Efficiency':
            if len(st.session_state.battery_charging_efficiency) != st.session_state.num_battery_types:
                st.session_state.battery_charging_efficiency = [0.0] * st.session_state.num_battery_types
            st.session_state.battery_charging_efficiency[i] = st.number_input(
                f"Battery Charging Efficiency [%]:", 
                min_value=0.0, 
                value=st.session_state.battery_charging_efficiency[i],
                key=f"battery_charging_efficiency_{i}"
            )
            if len(st.session_state.battery_discharging_efficiency) != st.session_state.num_battery_types:
                st.session_state.battery_discharging_efficiency = [0.0] * st.session_state.num_battery_types
            st.session_state.battery_discharging_efficiency[i] = st.number_input(
                f"Battery Discharging Efficiency [%]:", 
                min_value=0.0, 
                value=st.session_state.battery_discharging_efficiency[i],
                key=f"battery_discharging_efficiency_{i}"
            )
        else:
            if len(st.session_state.battery_roundtrip_efficiency) != st.session_state.num_battery_types:
                st.session_state.battery_roundtrip_efficiency = [0.0] * st.session_state.num_battery_types
            st.session_state.battery_roundtrip_efficiency[i] = st.number_input(
                f"Battery Roundtrip Efficiency [%]:", 
                min_value=0.0, 
                value=st.session_state.battery_roundtrip_efficiency[i],
                key=f"battery_roundtrip_efficiency_{i}"
            )
            st.session_state.battery_charging_efficiency[i] = float(np.sqrt(st.session_state.battery_roundtrip_efficiency[i]))
            st.session_state.battery_discharging_efficiency[i] = float(np.sqrt(st.session_state.battery_roundtrip_efficiency[i]))

        # Battery Inverter Efficiency (if needed)
        if not st.session_state.battery_inverter_eff_included:
            if not st.session_state.battery_dynamic_inverter_efficiency:
                if len(st.session_state.battery_inverter_efficiency) != st.session_state.num_battery_types:
                    st.session_state.battery_inverter_efficiency = [0.0] * st.session_state.num_battery_types
                st.session_state.battery_inverter_efficiency[i] = st.number_input(
                    f"Inverter Efficiency [%]:", 
                    min_value=0.0, 
                    value=st.session_state.battery_inverter_efficiency[i],
                    key=f"battery_inverter_efficiency_{i}"
                )

        # Battery Temporal Degradation Rate (if needed)
        if st.session_state.battery_temporal_degradation:
            if len(st.session_state.battery_temporal_degradation_rate) != st.session_state.num_battery_types:
                st.session_state.battery_temporal_degradation_rate = [0.0] * st.session_state.num_battery_types
            battery_temporal_degradation_rate = st.number_input(
                f"Degradation Rate [% per year]:", 
                min_value=0.0, 
                value=st.session_state.battery_temporal_degradation_rate[i],
                key = f"battery_temporal_degradation_rate_{i}"
            )
            st.session_state.battery_temporal_degradation_rate[i] = battery_temporal_degradation_rate

            if len(st.session_state.battery_temporal_degradation_rate) != st.session_state.num_battery_types:
                st.session_state.battery_temporal_degradation_rate = [0.0] * st.session_state.num_battery_types

        # Battery Cyclic Degradation Rate (if needed)
        if st.session_state.battery_cyclic_degradation:
            st.session_state.battery_chemistry[i] = st.selectbox(
                "Battery Chemistry:",
                ['LFP - Lithium Iron Phosphate (LFP)', 'NCA- Lithium Nickel Cobalt Aluminum Oxide', 'LMO -Lithium Manganese Oxide', 'NMC (Lithium Nickel Manganese Cobalt Oxide)'],
                index=0
            )
            if st.session_state.battery_chemistry[i] == 'LFP - Lithium Iron Phosphate (LFP)':
                Names = ['Sony-Murata 3 Ah LFP-Gr cylindrical cells', 'Large-format prismatic commercial LFP-Gr']
                Models = ['Lfp_Gr_SonyMurata3Ah_Battery', 'Lfp_Gr_250AhPrismatic']

            if st.session_state.battery_chemistry[i] == 'NCA- Lithium Nickel Cobalt Aluminum Oxide':
                Names = ['Panasonic 18650B NCA-Gr (3Ah)', 'Sony-Murata US18650VTC5A 3.5 Ah NCA-GrSi cylindrical cells']
                Models = ['Nca_Gr_Panasonic3Ah_Battery', 'NCA_GrSi_SonyMurata2p5Ah_Battery']

            if st.session_state.battery_chemistry[i] == 'LMO -Lithium Manganese Oxide':
                Names = ['Nissan Leaf LMO-Gr Battery  by Braco (66Ah, 2nd Life Cells)']
                Models = ['Lmo_Gr_NissanLeaf66Ah_2ndLife_Battery']

            if st.session_state.battery_chemistry[i] == 'NMC (Lithium Nickel Manganese Cobalt Oxide)':
                Names = ['Commercial NMC-LT0', 'Kokam 75 Ah NMC-Gr pouch cell', 'Sanyo UR18650E cells (2Ah)', 'NMC622-Gr EV cells from DENSO',
                            'LG MJ1 cell (4Ah)', 'Large format pouch NMC-Gr B1 cells', 'Large format pouch NMC-Gr B2 cells', 'Large format pouch NMC-Gr A cells',
                            'NMC-LTO cells']
                Models = ['Nmc_Lto_10Ah_Battery', 'Nmc111_Gr_Kokam75Ah_Battery', 'Nmc111_Gr_Sanyo2Ah_Battery', 'Nmc622_Gr_DENSO50Ah_Battery',
                            ' Nmc811_GrSi_LGMJ1_4Ah_Battery', 'NMC_Gr_50Ah_B1', 'NMC_Gr_50Ah_B2', 'NMC_Gr_75Ah_A',
                            'Nmc_Lto_10Ah_Battery']
                
            battery_model_name = st.selectbox(
                "Battery Model:",
                Names,
                index=Models.index(st.session_state.battery_model[i])
            )
            st.session_state.battery_model[i] = Models[Names.index(battery_model_name)]

    
    if st.session_state.economic_validation:
        # Battery Investment Cost
        if len(st.session_state.battery_investment_cost) != st.session_state.num_battery_types:
            st.session_state.battery_investment_cost = [0.0] * st.session_state.num_battery_types
        st.session_state.battery_investment_cost[i] = st.number_input(
            f"Investment Cost [USD]:", 
            min_value=0.0, 
            value=st.session_state.battery_investment_cost[i],
            key=f"battery_investment_cost_{i}"
        )

        # Battery Yearly Operation and Maintenance Cost
        if len(st.session_state.battery_maintenance_cost) != st.session_state.num_battery_types:
            st.session_state.battery_maintenance_cost = [0.0] * st.session_state.num_battery_types
        st.session_state.battery_maintenance_cost[i] = st.number_input(
            f"Yearly Operation and Maintenance Cost [USD/year]:", 
            min_value=0.0, 
            value=st.session_state.battery_maintenance_cost[i],
            key=f"battery_maintenance_cost_{i}"
        )

    if st.button("Close"):
        st.rerun()


# Function to render the battery configuration page
def battery() -> None:
    """Streamlit page for configuring battery parameters."""
    st.title("Battery")
    st.subheader("Define the parameters for the Batteries")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'battery_parameters')

    # Number of battery units
    st.session_state.battery_num_units = st.number_input("Enter the number of units", min_value=1, value = st.session_state.battery_num_units)
    
    # Installation dates
    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.battery_installation_dates) != st.session_state.battery_num_units:
        st.session_state.battery_installation_dates = [dt.datetime.now() for _ in range(st.session_state.battery_num_units)]
    # Installation dates selection
    with st.expander(f"Installation Dates", expanded=False):
        st.session_state.selected_timezone_battery = timezone_selector()
        if st.session_state.battery_num_units > 1:
            # Checkbox to determine if the installation date is the same for all units
            st.session_state.battery_same_date = st.checkbox("Same installation date for all units", 
                        value = st.session_state.battery_same_date)
            
            if st.session_state.battery_same_date:
                # Asign same date to all units
                if 'installation_dates' not in st.session_state or len(st.session_state.battery_installation_dates) != st.session_state.battery_num_units:
                    today_midnight = dt.datetime.combine(dt.date.today(), dt.time.min)
                    st.session_state.battery_installation_dates = [today_midnight for _ in range(st.session_state.battery_num_units)]
                col1, col2 = st.columns(2)
                with col1:
                    same_installation_date = st.date_input(
                        "Installation Date",
                        value=st.session_state.battery_installation_dates[0].date() if st.session_state.battery_installation_dates[0] else dt.datetime.now().date()
                    )
                with col2:
                    same_installation_time = st.time_input(
                        "Installation Time",
                        value=st.session_state.battery_installation_dates[0].time() if st.session_state.installation_dates[0] else dt.time.min
                    )
                # Combine date and time
                same_installation_datetime = combine_date_and_time(same_installation_date, same_installation_time)
                # Set the same datetime for all units
                for i in range(st.session_state.battery_num_units):
                    st.session_state.battery_installation_dates[i] = same_installation_datetime
            else:
                # Multiple date inputs for each unit                
                for i in range(st.session_state.battery_num_units):
                # Create a date and time input for each unit
                    col1, col2 = st.columns(2)
                    with col1:
                        input_date = st.date_input(
                            f"Installation Date for Unit {i + 1}",
                            value=st.session_state.battery_installation_dates[i].date() if st.session_state.battery_installation_dates else dt.datetime.now().date(),
                            key=f"date_input_{i}"
                        )
                    with col2:
                        input_time = st.time_input(
                            f"Installation Time for Unit {i + 1}",
                            value=st.session_state.battery_installation_dates[i].time() if st.session_state.battery_installation_dates else dt.time.min,
                            key=f"time_input_{i}"
                        )
                    # Combine date and time into a datetime object
                    st.session_state.battery_installation_dates[i] = combine_date_and_time(input_date, input_time)
        else:
            # Single date input for one unit
            st.write("Enter the installation date for the unit:")
            col1, col2 = st.columns(2)
            with col1:
                input_date = st.date_input(
                    "Installation Date",
                    value=st.session_state.battery_installation_dates[0].date() if st.session_state.battery_installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min)
                )
            with col2:
                input_time = st.time_input(
                    "Installation Time",
                    value=st.session_state.battery_installation_dates[0].time() if st.session_state.battery_installation_dates else dt.time.min
                )
            # Combine date and time into a datetime object
            st.session_state.battery_installation_dates[0] = combine_date_and_time(input_date, input_time)
        # Convert installation dates to UTC
        st.session_state.battery_installation_dates_utc = convert_dates_to_utc(st.session_state.battery_installation_dates, st.session_state.selected_timezone_battery)

    # Battery types selection
    if len(st.session_state.battery_type) != st.session_state.battery_num_units:
        st.session_state.battery_type = [None] * st.session_state.battery_num_units
    if st.session_state.battery_num_units > 1:
        st.write("Enter the number of PV types that were used:")
        # Checkbox to determine if the type is the same for all units
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.battery_same_type = st.checkbox("Same type for all units", value = st.session_state.battery_same_type)
        
        if st.session_state.battery_same_type:
            # Select Type 1 for all units
            st.session_state.num_battery_types = 1
            st.session_state.battery_types = ['Type 1']  
            for i in range(st.session_state.battery_num_units):
                st.session_state.battery_type[i] = st.session_state.battery_types[0]
        
        else:
            # Input the number of types
            with col2:
                st.session_state.num_battery_types = st.number_input("Enter the number of types", min_value=2, max_value=st.session_state.battery_num_units, value = max(st.session_state.num_battery_types,2))
            st.session_state.battery_types = [None] * st.session_state.num_battery_types
            for i in range(st.session_state.num_battery_types):
                st.session_state.battery_types[i] = f'Type {i+1}'

            col1, col2 = st.columns(2)
            for i in range(st.session_state.battery_num_units):
                # Create a dropdown to select type for each unit
                col = col1 if i % 2 == 0 else col2
                with col:
                    selected_value = st.session_state.battery_type[i] if st.session_state.battery_type[i] else st.session_state.battery_types[0]
                    selected_index = st.session_state.battery_types.index(selected_value)
                    st.session_state.battery_type[i] = st.selectbox(
                        f"Type for Unit {i + 1}",
                        st.session_state.battery_types,
                        index=selected_index,
                        key=f"type_select_{i}"
                    )
    else:
        # If there's only one unit, default Type 1 for that unit
        st.session_state.num_battery_types = 1
        st.session_state.battery_types = ['Type 1']        
        st.session_state.battery_type[0] = st.session_state.battery_types[0]


    if st.session_state.technical_validation:
        # Let choose Battery Efficiency option
        options = ['Seperate Charging and Discharging Efficiency', 'Roundtrip Efficiency']
        st.session_state.battery_efficiency_type = st.selectbox(
            'Battery Efficiency:',
            options,
            index = options.index(st.session_state.battery_efficiency_type))

        # Let choose what was included in the calculations    
        options = ['Temporal battery degradation', 'Cyclic battery degradation', 'Inverter efficiency included in the battery efficiency']

        if st.session_state.battery_inverter_eff_included:
            options.append('Dynamic inverter efficiency')
        options_selected = []
        if st.session_state.battery_temporal_degradation:
            options_selected.append('Temporal battery degradation')
        if st.session_state.battery_cyclic_degradation:
            options_selected.append('Cyclic battery degradation')
        if st.session_state.battery_inverter_eff_included:
            options_selected.append('Inverter efficiency included in the battery efficiency')
        if st.session_state.battery_dynamic_inverter_efficiency:
            options_selected.append('Dynamic inverter efficiency')
        
        included = st.pills(
            "Choose what was included in your calculations:", 
            options=options,
            default=options_selected,
            selection_mode='multi')

        st.session_state.battery_temporal_degradation = 'Temporal battery degradation' in included
        st.session_state.battery_cyclic_degradation = 'Cyclic battery degradation' in included
        st.session_state.battery_inverter_eff_included = 'Inverter efficiency included in the battery efficiency' in included
        if st.session_state.battery_inverter_eff_included:
            st.session_state.battery_dynamic_inverter_efficiency = 'Dynamic inverter efficiency' in included
        else:
            st.session_state.battery_dynamic_inverter_efficiency = False


    # Display the input fields for each battery type
    st.write("Enter Battery parameters:")
    col1, col2 = st.columns(2)
    for i in range(st.session_state.num_battery_types):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(f"Enter Battery Specifications for Type {i+1}"):
                enter_specifications(i)