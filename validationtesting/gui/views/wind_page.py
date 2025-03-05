"""
This file contains the code for the Wind page of the GUI.
The user can specify the specifications for the wind energy.
"""

import streamlit as st
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, csv_upload_interface, combine_date_and_time, load_csv_data
import datetime as dt
import pandas as pd

@st.dialog("Enter Wind Energy Specifications")
def enter_specifications(i: int) -> None:
    """
    Displays input fields for entering wind energy specifications for a given wind energy type.
    This function dynamically generates input fields for various wind energy specifications based on the
    current state of the application. It handles both technical and economic validation scenarios.
    """
    st.write(f"Enter Wind Energy Specifications for Type {i+1}.")

    # Initialize wind_lifetime if necessary
    if len(st.session_state.wind_lifetime) < st.session_state.num_wind_types:
        st.session_state.wind_lifetime.extend([0] * (st.session_state.num_wind_types - len(st.session_state.wind_lifetime)))
    st.session_state.wind_lifetime[i] = st.number_input(f"Lifetime [in years]:", 
        min_value=0, 
        value=st.session_state.wind_lifetime[i],
        key=f"wind_lifetime_{i}"
    )

    if st.session_state.technical_validation:

        # Rated Power
        if len(st.session_state.wind_rated_power) < st.session_state.num_wind_types:
            st.session_state.wind_rated_power.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_rated_power)))
        st.session_state.wind_rated_power[i] = st.number_input(f"Rated Power [W]:", 
            min_value=0.0, 
            value=st.session_state.wind_rated_power[i],
            key=f"wind_rated_power_{i}"
        )

        # Drivetrain Efficiency
        if len(st.session_state.wind_drivetrain_efficiency) < st.session_state.num_wind_types:
            st.session_state.wind_drivetrain_efficiency.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_drivetrain_efficiency)))
        st.session_state.wind_drivetrain_efficiency[i] = st.number_input(f"Drive Train Efficiency [%]:", 
            min_value=0.0,
            value=st.session_state.wind_drivetrain_efficiency[i],
            key=f"wind_drivetrain_efficiency_{i}"
        )

        # Hub Height
        if len(st.session_state.wind_hub_height) < st.session_state.num_wind_types:
            st.session_state.wind_hub_height.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_hub_height)))
        st.session_state.wind_hub_height[i] = st.number_input(f"Hub Height [m]:", 
            min_value=0.0, 
            value=st.session_state.wind_hub_height[i],
            key=f"wind_hub_height_{i}"
        )

        # Temporal Degradation Rate
        if st.session_state.wind_temporal_degradation:
            if len(st.session_state.wind_temporal_degradation_rate) < st.session_state.num_wind_types:
                st.session_state.wind_temporal_degradation_rate.extend([0.0] * (st.session_state.num_wind_types - len(st.session_state.wind_temporal_degradation_rate)))
            st.session_state.wind_temporal_degradation_rate[i] = st.number_input(
                f"Degradation Rate [%/year]:", 
                min_value=0.0, 
                value=st.session_state.wind_temporal_degradation_rate[i],
                key=f"wind_degradation_rate_{i}"
            )

        # Wind Power Curve
        project_name = st.session_state.get("project_name")
        wind_power_curve_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"wind_power_curve_type_{i+1}.csv"
        if len(st.session_state.wind_power_curve_uploaded) < st.session_state.num_wind_types:
            st.session_state.wind_power_curve_uploaded.extend([False] * (st.session_state.num_wind_types - len(st.session_state.wind_power_curve_uploaded)))
        if st.session_state.wind_power_curve_uploaded[i]:
            # Load the uploaded CSV file into a DataFrame
            df = pd.read_csv(wind_power_curve_path)
        else:
            selected_upload_type = st.selectbox(
                f"Select the way to upload the power curve", 
                ['Enter manually', 'Upload a CSV file'])
            if selected_upload_type == 'Enter manually':
            # If no file is uploaded, create a default DataFrame
                df = pd.DataFrame({
                    'Wind Speed [m/s]': [],
                    'Power [W]': []
                })
            elif selected_upload_type == 'Upload a CSV file':
                uploaded_file, delimiter, decimal = csv_upload_interface(f"power_curve_{i}")
                if uploaded_file:
                    data_dict = {}
                    wind_speed_power_curve = load_csv_data(uploaded_file, delimiter, decimal, f'Wind Speed [m/s]')
                    data_dict[f'Wind Speed [m/s]'] = wind_speed_power_curve.values.flatten() if wind_speed_power_curve is not None else None
                    col1, col2 = st.columns(2)
                    with col1:
                        power_power_curve = load_csv_data(uploaded_file, delimiter, decimal, f'Power')
                    with col2:
                        energy_unit = st.selectbox(
                                f"Select the unit of the Power:",
                                ['W', 'kW', 'MW']
                            ) 
                        if energy_unit == 'kW':
                            power_power_curve = power_power_curve * 1e3
                        elif energy_unit == 'MW':
                            power_power_curve = power_power_curve * 1e6
                    data_dict[f'Power [W]'] = power_power_curve.values.flatten() if power_power_curve is not None else None
                    df = pd.DataFrame(data_dict)
        if st.session_state.wind_power_curve_uploaded[i] or selected_upload_type == 'Enter manually' or uploaded_file:
            # Display the table for editing
            edited_table = st.data_editor(
                df,
                num_rows="dynamic",  # Allows adding/removing rows
                use_container_width=True,
                key="csv_table_editor"
            )

    # Economic Validation
    if st.session_state.economic_validation:
        # Investment Cost
        col1, col2 = st.columns(2)
        with col1:
            if len(st.session_state.wind_investment_cost) != st.session_state.num_wind_types:
                st.session_state.wind_investment_cost = [0.0] * st.session_state.num_wind_types
            st.session_state.wind_investment_cost[i] = st.number_input(
                f"Investment Cost []:", 
                min_value=0.0, 
                value=st.session_state.wind_investment_cost[i],
                key=f"wind_investment_cost_{i}"
            )
        with col2:
            if len(st.session_state.wind_exclude_investment_cost) != st.session_state.num_wind_types:
                st.session_state.wind_exclude_investment_cost = [False] * st.session_state.num_wind_types
            st.session_state.wind_exclude_investment_cost[i] = st.checkbox(
                "Exclude Investment Cost", 
                value = st.session_state.wind_exclude_investment_cost[i])

        # Yearly Operation and Maintenance Cost
        if len(st.session_state.wind_maintenance_cost) != st.session_state.num_wind_types:
            st.session_state.wind_maintenance_cost = [0.0] * st.session_state.num_wind_types
        st.session_state.wind_maintenance_cost[i] = st.number_input(
            f"Yearly Operation and Maintenance Cost [% of investment cost per year]:", 
            min_value=0.0, 
            value=st.session_state.wind_maintenance_cost[i],
            key=f"wind_maintenance_cost_{i}"
        )

        # End of Project Cost
        if len(st.session_state.wind_end_of_project_cost) != st.session_state.num_wind_types:
            st.session_state.wind_end_of_project_cost = [0.0] * st.session_state.num_wind_types
        st.session_state.wind_end_of_project_cost[i] = st.number_input(
            f"End of Project Cost []:", 
            min_value=0.0, 
            value=st.session_state.wind_end_of_project_cost[i],
            key=f"wind_end_of_project_cost_{i}"
        )

    if st.button("Close"):
        if st.session_state.technical_validation:
            # Store the combined data in session state
            st.session_state.wind_power_curve_uploaded[i] = True  # Set the flag to True since data is now uploaded
            sorted_table = edited_table.sort_values(by='Wind Speed [m/s]')
            sorted_table.to_csv(wind_power_curve_path, index=False)
        st.rerun()


def wind() -> None:
    """Streamlit page for configuring renewable energy technology parameters."""
    st.title("Wind Energy")
    st.subheader("Define the parameters for the Wind Energy")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'wind_parameters')
    st.session_state.wind_num_units = st.number_input("Enter the number of Wind Energy units", min_value=1, value=st.session_state.wind_num_units)
    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.wind_installation_dates) != st.session_state.wind_num_units:
        st.session_state.wind_installation_dates = [dt.datetime.now() for _ in range(st.session_state.wind_num_units)]

    with st.expander(f"Installation Dates", expanded=False):
        if st.session_state.wind_num_units > 1:
            # Checkbox to determine if the installation date is the same for all units
            st.session_state.wind_same_date = st.checkbox("Same installation date for all units", value=st.session_state.wind_same_date)

            if st.session_state.wind_same_date:
                if 'installation_dates' not in st.session_state or len(st.session_state.wind_installation_dates) != st.session_state.wind_num_units:
                    # Initialize with today's date at 00:00
                    today_midnight = dt.datetime.combine(dt.date.today(), dt.time.min)  # Today's date at 00:00
                    st.session_state.wind_installation_dates = [today_midnight for _ in range(st.session_state.wind_num_units)]

                # Single date and time input for all units
                same_installation_date = st.date_input(
                    "Installation Date",
                    value=st.session_state.wind_installation_dates[0].date() if st.session_state.wind_installation_dates[0] else dt.datetime.combine(dt.date.today(), dt.time.min)
                )

                
                # Combine date and time
                same_installation_datetime = combine_date_and_time(same_installation_date)
                
                # Set the same datetime for all units
                for i in range(st.session_state.wind_num_units):
                    st.session_state.wind_installation_dates[i] = same_installation_datetime
            else:
                # Multiple date inputs for each unit                
                for i in range(st.session_state.wind_num_units):
                # Create a date and time input for each unit
                    input_date = st.date_input(
                        f"Installation Date for Unit {i + 1}",
                        value=st.session_state.wind_installation_dates[i].date() if st.session_state.wind_installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min),
                        key=f"date_input_{i}"
                    )
                    
                    # Combine date and time into a datetime object
                    st.session_state.wind_installation_dates[i] = combine_date_and_time(input_date)
        else:
            # Only one unit, so no checkbox needed
            st.write("Enter the installation date for the unit:")
            input_date = st.date_input(
                "Installation Date",
                value=st.session_state.wind_installation_dates[0].date() if st.session_state.wind_installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min)
            )

            # Combine date and time into a datetime object
            st.session_state.wind_installation_dates[0] = combine_date_and_time(input_date)
        
    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.wind_type) != st.session_state.wind_num_units:
        st.session_state.wind_type = [None] * st.session_state.wind_num_units

    if st.session_state.wind_num_units > 1:
        st.write("Enter the number of PV types that were used:")
        # Checkbox to determine if the type is the same for all units
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.wind_same_type = st.checkbox("Same type for all units", value=st.session_state.wind_same_type)

        if st.session_state.wind_same_type:
            # Select the same type for all units
            st.session_state.num_wind_types = 1
            st.session_state.wind_types = ['Type 1']  
            for i in range(st.session_state.wind_num_units):
                st.session_state.wind_type[i] = st.session_state.wind_types[0]
        else:
            with col2:
                st.session_state.num_wind_types = st.number_input("Enter the number of types", min_value=2, max_value=st.session_state.wind_num_units, value=max(st.session_state.num_wind_types,2))
            st.session_state.wind_types = [None] * st.session_state.num_wind_types
            for i in range(st.session_state.num_wind_types):
                st.session_state.wind_types[i] = f'Type {i+1}'

            # Multiple select boxes for each unit
            col1, col2 = st.columns(2)
            for i in range(st.session_state.wind_num_units):
                col = col1 if i % 2 == 0 else col2
                with col:
                    # Create a dropdown to select type for each unit
                    selected_value = st.session_state.wind_type[i] if st.session_state.wind_type[i] else st.session_state.wind_types[0]
                    selected_index = st.session_state.wind_types.index(selected_value)
                    st.session_state.wind_type[i] = st.selectbox(
                        f"Type for Unit {i + 1}",
                        st.session_state.wind_types,
                        index=selected_index,
                        key=f"type_select_{i}"
                    )
    else:
        # If there's only one unit, default to selecting a type for that unit
        st.session_state.num_wind_types = 1
        st.session_state.wind_types = ['Type 1']        
        st.session_state.wind_type[0] = st.session_state.wind_types[0]

    if st.session_state.technical_validation:
        st.session_state.wind_temporal_degradation = st.checkbox("Temporal wind turbine degradation", value=st.session_state.wind_temporal_degradation)

    # Display the input fields for each type
    st.write("Enter the specifications for each wind turbine type:")
    col1, col2 = st.columns(2)
    for i in range(st.session_state.num_wind_types):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(f"Enter Wind Specifications for Type {i+1}"):
                enter_specifications(i)