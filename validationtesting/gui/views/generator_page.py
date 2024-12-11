import streamlit as st
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state, timezone_selector
import datetime as dt
import pytz
import pandas as pd
import numpy as np

@st.dialog("Enter Generator Specifications")
def enter_specifications(i: int) -> None:
    st.write(f"Enter Generator Specifications for Type {i+1}.")

    if len(st.session_state.generator_lifetime) != st.session_state.num_generator_types:
        st.session_state.generator_lifetime.extend([0] * (st.session_state.num_generator_types - len(st.session_state.generator_lifetime)))
    st.session_state.generator_lifetime[i] = st.number_input(
        f"Generator Lifetime [years]:", 
        min_value=0, 
        value=st.session_state.generator_lifetime[i],
        key=f"generator_lifetime_{i}"
    )

    if st.session_state.technical_validation:

        if not st.session_state.generator_dynamic_efficiency:
            if len(st.session_state.generator_efficiency) != st.session_state.num_generator_types:
                st.session_state.generator_efficiency.extend([0.0] * (st.session_state.num_generator_types - len(st.session_state.generator_efficiency)))
            st.session_state.generator_efficiency[i] = st.number_input(
                f"Generator efficiency [%]:", 
                min_value=0.0, 
                value=st.session_state.generator_efficiency[i],
                key=f"generator_efficiency_{i}"
            )

        if len(st.session_state.generator_min_power) != st.session_state.num_generator_types:
            st.session_state.generator_min_power.extend([0.0] * (st.session_state.num_generator_types - len(st.session_state.generator_min_power)))
        st.session_state.generator_min_power[i] = st.number_input(
            f"Minimum Power [W]:", 
            min_value=0.0, 
            value=st.session_state.generator_min_power[i],
            key=f"generator_min_power_{i}"
        )
        
        if len(st.session_state.generator_max_power) != st.session_state.num_generator_types:
            st.session_state.generator_max_power.extend([0.0] * (st.session_state.num_generator_types - len(st.session_state.generator_max_power)))
        st.session_state.generator_max_power[i] = st.number_input(
            f"Maximum Power [W]:", 
            min_value=0.0, 
            value=st.session_state.generator_max_power[i],
            key=f"generator_max_power_{i}"
        )

        if len(st.session_state.generator_fuel_lhv) != st.session_state.num_generator_types:
            st.session_state.generator_fuel_lhv.extend([0.0] * (st.session_state.num_generator_types - len(st.session_state.generator_fuel_lhv)))
        st.session_state.generator_fuel_lhv[i] = st.number_input(
            f"Fuel LHV [Wh/l]:", 
            min_value=0.0, 
            value=st.session_state.generator_fuel_lhv[i],
            key=f"generator_fuel_lhv_{i}"
        )

        if st.session_state.generator_temporal_degradation:
            if len(st.session_state.generator_temporal_degradation_rate) != st.session_state.num_generator_types:
                st.session_state.generator_temporal_degradation_rate.extend([0.0] * (st.session_state.num_generator_types - len(st.session_state.generator_temporal_degradation_rate)))
            st.session_state.generator_temporal_degradation_rate[i] = st.number_input(
                f"Degradation Rate [% per year]:", 
                min_value=0.0, 
                value=st.session_state.generator_temporal_degradation_rate[i],
                key=f"generator_degradation_rate_{i}"
            )
        
        if st.session_state.generator_dynamic_efficiency:
            if len(st.session_state.generator_dynamic_efficiency_type) != st.session_state.num_generator_types:
                st.session_state.generator_dynamic_efficiency_type.extend([None] * (st.session_state.num_generator_types - len(st.session_state.generator_dynamic_efficiency_type)))
            st.session_state.generator_dynamic_efficiency_type[i] = st.selectbox(
                "Select Input Type",
                [
                    "Tabular Data", 
                    "Formula"
                ],
                index=["Tabular Data", "Formula"].index(st.session_state.generator_dynamic_efficiency_type[i]) if st.session_state.generator_dynamic_efficiency_type[i] in ["Tabular Data", "Formula"] else 0,
                key=f"generator_dynamic_efficiency_type_{i}"
            )

            if st.session_state.generator_dynamic_efficiency_type[i] == "Tabular Data":
                project_name = st.session_state.get("project_name")
                dynamic_efficiency_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"generator_dynamic_efficiency_type_{i+1}.csv"
                if st.session_state.generator_dynamic_efficiency_uploaded[i]:
                    # Load the uploaded CSV file into a DataFrame
                    df = pd.read_csv(dynamic_efficiency_path)
                else:
                    # If no file is uploaded, create a default DataFrame
                    df = pd.DataFrame({
                        'Load': [st.session_state.generator_min_power[i], st.session_state.generator_max_power[i]],
                        'Efficiency (%)': [20, 30]
                    })

                # Display the table for editing
                edited_table = st.data_editor(
                    df,
                    num_rows="dynamic",  # Allows adding/removing rows
                    use_container_width=True,
                    key="csv_table_editor"
                )

            else:
                st.session_state.generator_efficiency_formula[i] = st.text_input(
                    f"Generator Efficiency Formula:", 
                    value=st.session_state.generator_efficiency_formula[i] if st.session_state.generator_efficiency_formula[i] else f"30 * (P / {st.session_state.generator_max_power[i]})",
                    key=f"generator_efficiency_formula_{i}"
                )

    if st.session_state.economic_validation:
        # generator Investment Cost
        if len(st.session_state.generator_investment_cost) != st.session_state.num_generator_types:
            st.session_state.generator_investment_cost = [0.0] * st.session_state.num_generator_types
        st.session_state.generator_investment_cost[i] = st.number_input(
            f"Investment Cost [USD]:", 
            min_value=0.0, 
            value=st.session_state.generator_investment_cost[i],
            key=f"generator_investment_cost_{i}"
        )

        # generator Yearly Operation and Maintenance Cost
        if len(st.session_state.generator_maintenance_cost) != st.session_state.num_generator_types:
            st.session_state.generator_maintenance_cost = [0.0] * st.session_state.num_generator_types
        st.session_state.generator_maintenance_cost[i] = st.number_input(
            f"Yearly Operation and Maintenance Cost [USD/year]:", 
            min_value=0.0, 
            value=st.session_state.generator_maintenance_cost[i],
            key=f"generator_maintenance_cost_{i}"
        )

    if st.button("Close"):
        st.session_state.generator_dynamic_efficiency_uploaded[i] = True  # Set the flag to True since data is now uploaded
        if st.session_state.generator_dynamic_efficiency:
            if st.session_state.generator_dynamic_efficiency_type[i] == "Tabular Data":
                sorted_table = edited_table.sort_values(by='Load')
                sorted_table.to_csv(dynamic_efficiency_path, index=False)
        st.rerun()

# Function to convert installation dates to UTC
def convert_dates_to_utc(installation_dates: list[dt.datetime], timezone_str: str) -> list[dt.datetime]:
    # Load the timezone
    local_tz = pytz.timezone(timezone_str)

    # Convert each date to UTC
    installation_dates_utc = []
    for date in installation_dates:
        if isinstance(date, dt.datetime):
            # Localize the date to the selected timezone and convert to UTC
            localized_date = local_tz.localize(date)
            utc_date = localized_date.astimezone(pytz.UTC).replace(tzinfo=None)
            installation_dates_utc.append(utc_date)
        else:
            installation_dates_utc.append(None)  # Handle cases where date is not provided

    return installation_dates_utc

def combine_date_and_time(date_value: dt.date, time_value: dt.time) -> dt.datetime:
    """Combine date and time into a datetime object."""
    return dt.datetime.combine(date_value, time_value)

def generator() -> None:
    """Streamlit page for configuring renewable energy technology parameters."""
    st.title("Generator")
    st.subheader("Define the parameters for the Generators")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'generator_parameters')
    st.session_state.generator_num_units = st.number_input("Enter the number of generator units", min_value=1, value=st.session_state.generator_num_units)
    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.generator_installation_dates) != st.session_state.generator_num_units:
        st.session_state.generator_installation_dates = [dt.datetime.now() for _ in range(st.session_state.generator_num_units)]

    with st.expander(f"Installation Dates", expanded=False):
        st.session_state.selected_timezone_generator = timezone_selector()
        if st.session_state.generator_num_units > 1:
            # Checkbox to determine if the installation date is the same for all units
            st.session_state.generator_same_date = st.checkbox(
                "Same installation date for all units", 
                value = st.session_state.generator_same_date)

            if st.session_state.generator_same_date:
                if 'installation_dates' not in st.session_state or len(st.session_state.generator_installation_dates) != st.session_state.generator_num_units:
                    # Initialize with today's date at 00:00
                    today_midnight = dt.datetime.combine(dt.date.today(), dt.time.min)  # Today's date at 00:00
                    st.session_state.generator_installation_dates = [today_midnight for _ in range(st.session_state.generator_num_units)]

                # Single date and time input for all units
                col1, col2 = st.columns(2)
                with col1:
                    same_installation_date = st.date_input(
                        "Installation Date",
                        value=st.session_state.generator_installation_dates[0].date() if st.session_state.generator_installation_dates[0] else dt.datetime.combine(dt.date.today(), dt.time.min)
                    )
                with col2:
                    same_installation_time = st.time_input(
                        "Installation Time",
                        value=st.session_state.generator_installation_dates[0].time() #if st.session_state.installation_dates[0] else dt.datetime.now().time()
                    )
                
                # Combine date and time
                same_installation_datetime = combine_date_and_time(same_installation_date, same_installation_time)
                
                # Set the same datetime for all units
                for i in range(st.session_state.generator_num_units):
                    st.session_state.generator_installation_dates[i] = same_installation_datetime
            else:
                # Multiple date inputs for each unit                
                for i in range(st.session_state.generator_num_units):
                # Create a date and time input for each unit
                    col1, col2 = st.columns(2)
                    with col1:
                        input_date = st.date_input(
                            f"Installation Date for Unit {i + 1}",
                            value=st.session_state.generator_installation_dates[i].date() if st.session_state.generator_installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min),
                            key=f"date_input_{i}"
                        )
                    with col2:
                        input_time = st.time_input(
                            f"Installation Time for Unit {i + 1}",
                            value=st.session_state.generator_installation_dates[i].time() if st.session_state.generator_installation_dates else dt.time.min,
                            key=f"time_input_{i}"
                        )
                    
                    # Combine date and time into a datetime object
                    st.session_state.generator_installation_dates[i] = combine_date_and_time(input_date, input_time)
        else:
            # Only one unit, so no checkbox needed
            st.write("Enter the installation date for the unit:")
            col1, col2 = st.columns(2)
            with col1:
                input_date = st.date_input(
                    "Installation Date",
                    value=st.session_state.generator_installation_dates[0].date() if st.session_state.generator_installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min)
                )
            with col2:
                input_time = st.time_input(
                    "Installation Time",
                    value=st.session_state.generator_installation_dates[0].time() if st.session_state.generator_installation_dates else dt.time.min
                )
            
            # Combine date and time into a datetime object
            st.session_state.generator_installation_dates[0] = combine_date_and_time(input_date, input_time)
        
        st.session_state.generator_installation_dates_utc = convert_dates_to_utc(st.session_state.generator_installation_dates, st.session_state.selected_timezone_generator)

    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.generator_type) != st.session_state.generator_num_units:
        st.session_state.generator_type = [None] * st.session_state.generator_num_units

    if st.session_state.generator_num_units > 1:
        st.write("Enter the number of PV types that were used:")
        col1, col2 = st.columns(2)
        # Checkbox to determine if the type is the same for all units
        with col1:
            st.session_state.generator_same_type = st.checkbox(
                "Same type for all units", 
            value = st.session_state.generator_same_type)

        if st.session_state.generator_same_type:
            # Select the same type for all units
            st.session_state.num_generator_types = 1
            st.session_state.generator_types = ['Type 1']  
            for i in range(st.session_state.generator_num_units):
                st.session_state.generator_type[i] = st.session_state.generator_types[0]
        else:
            with col2:
                st.session_state.num_generator_types = st.number_input("Enter the number of types", min_value=2, max_value=st.session_state.generator_num_units, value=max(st.session_state.num_generator_types,2))
            st.session_state.generator_types = [None] * st.session_state.num_generator_types
            for i in range(st.session_state.num_generator_types):
                st.session_state.generator_types[i] = f'Type {i+1}'

            # Multiple select boxes for each unit
            col1, col2 = st.columns(2)
            for i in range(st.session_state.generator_num_units):
                # Create a dropdown to select type for each unit
                col = col1 if i % 2 == 0 else col2
                with col:
                    selected_value = st.session_state.generator_type[i] if st.session_state.generator_type[i] else st.session_state.generator_types[0]
                    selected_index = st.session_state.generator_types.index(selected_value)
                    st.session_state.generator_type[i] = st.selectbox(
                        f"Type for Unit {i + 1}",
                        st.session_state.generator_types,
                        index=selected_index,
                        key=f"type_select_{i}"
                    )
    else:
        # If there's only one unit, default to selecting a type for that unit
        st.session_state.num_generator_types = 1
        st.session_state.generator_types = ['Type 1']        
        st.session_state.generator_type[0] = st.session_state.generator_types[0]

    if st.session_state.technical_validation:
        st.write("Choose what was included in your calculations:")

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.generator_dynamic_efficiency = st.checkbox(
                "Dynamic inverter efficency", 
                value = st.session_state.generator_dynamic_efficiency)

            st.session_state.generator_temporal_degradation = st.checkbox(
                "Temporal generator degradation",
                value = st.session_state.generator_temporal_degradation)

        with col2:
            st.session_state.generator_cyclic_degradation = st.checkbox(
                "Cyclic generator degradation", 
                value = st.session_state.generator_cyclic_degradation)
            
    if st.session_state.economic_validation:
        # generator fuel price
        st.session_state.generator_variable_fuel_price = st.checkbox("Variable Fuel Price", value=st.session_state.generator_variable_fuel_price)
        if st.session_state.generator_variable_fuel_price:
            project_name = st.session_state.get("project_name")
            fuel_price_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"generator_fuel_price.csv"
            try:
                # Load the uploaded CSV file into a DataFrame
                df = pd.read_csv(fuel_price_path)
            except:
                # Generate years from start_year to end_year
                start_year = st.session_state.get("start_date").year
                end_year = st.session_state.get("end_date").year
                years = list(range(start_year, end_year + 1))
                df = pd.DataFrame({
                    'Year': years,
                    'Fuel Price [$/l]': [0.0] * len(years)
                })
            df["Year"] = df["Year"].astype(str)
            # Display the table for editing
            edited_table = st.data_editor(
                df,
                num_rows="fixed",  # Disallow adding/removing rows
                use_container_width=True,
                key="fuel_price_table_editor"
            )

            edited_table.to_csv(fuel_price_path, index=False)

        else:
            st.session_state.generator_fuel_price = st.number_input(
                f"Fuel Price [USD/l]:", 
                min_value=0.0, 
                value=st.session_state.generator_fuel_price,
            )


    st.write("Enter Generator parameters:")
    col1, col2 = st.columns(2)
    for i in range(st.session_state.num_generator_types):
        col = col1 if i % 2 == 0 else col2
        with col:
            if st.button(f"Enter Generator Specifications for Type {i+1}"):
                enter_specifications(i)