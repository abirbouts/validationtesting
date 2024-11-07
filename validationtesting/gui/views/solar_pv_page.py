import streamlit as st
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state
import datetime as dt
import pytz

def render_timezone_selector():
    # List of all available time zones with country names
    timezones_with_countries = ["Universal Time Coordinated - UTC"]  # Manually add UTC at the beginning
    for country_code, timezones in pytz.country_timezones.items():
        country_name = pytz.country_names[country_code]
        for timezone in timezones:
            timezones_with_countries.append(f"{country_name} - {timezone}")

    # Select time zone from a comprehensive list with country names
    selected_timezone_with_country = st.selectbox("Select the time zone for the installation dates:", timezones_with_countries)

    # Extract just the timezone (without the country name)
    selected_timezone = selected_timezone_with_country.split(' - ')[1]

    # Show the selected timezone for confirmation
    st.write(f"Selected Timezone: {selected_timezone_with_country}")

    return selected_timezone

# Function to convert installation dates to UTC
def convert_dates_to_utc(installation_dates, timezone_str):
    # Load the timezone
    local_tz = pytz.timezone(timezone_str)

    # Convert each date to UTC
    installation_dates_utc = []
    for date in installation_dates:
        if isinstance(date, dt.datetime):
            # Localize the date to the selected timezone and convert to UTC
            localized_date = local_tz.localize(date)
            utc_date = localized_date.astimezone(pytz.UTC)
            installation_dates_utc.append(utc_date)
        else:
            installation_dates_utc.append(None)  # Handle cases where date is not provided

    return installation_dates_utc

def combine_date_and_time(date_value, time_value):
    """Combine date and time into a datetime object."""
    return dt.datetime.combine(date_value, time_value)

def ensure_list_length(key: str, length: int) -> None:
    """Ensure the list in session state has the required length."""
    if key not in st.session_state:
        st.session_state[key] = [0.0] * length
    else:
        st.session_state[key].extend([0.0] * (length - len(st.session_state[key])))

def update_parameters(i: int, res_name: str, time_horizon: int, brownfield: bool, land_availability: float, currency: str) -> None:
    """Update renewable parameters for the given index."""
    st.subheader(f"{res_name} Parameters")
    
    st.session_state.res_inverter_efficiency[i] = st.number_input(
        f"Inverter Efficiency [%]", 
        min_value=0.0, 
        max_value=100.0, 
        value=float(st.session_state.res_inverter_efficiency[i] * 100), 
        key=f"inv_eff_{i}") / 100
    
    if land_availability > 0:
        st.session_state.res_specific_area[i] = st.number_input(
            f"Specific Area [m2/kW]",
            min_value=0.0, 
            value=float(st.session_state.res_specific_area[i]), 
            key=f"spec_area_{i}")
    
    st.session_state.res_specific_investment_cost[i] = st.number_input(
        f"Specific Investment Cost [{currency}/W]", 
        min_value=0.0,
        value=float(st.session_state.res_specific_investment_cost[i]), 
        key=f"inv_cost_{i}")
    
    st.session_state.res_specific_om_cost[i] = st.number_input(
        f"Specific O&M Cost as % of investment cost [%]", 
        min_value=0.0, 
        max_value=100.0,
        value=float(st.session_state.res_specific_om_cost[i] * 100), 
        key=f"om_cost_{i}") / 100
    
    if brownfield:
        st.session_state.res_lifetime[i] = st.number_input(
            f"Lifetime [years]", 
            value=float(st.session_state.res_lifetime[i]), 
            key=f"lifetime_{i}")
    else:
        st.session_state.res_lifetime[i] = st.number_input(
            f"Lifetime [years]", 
            min_value=float(time_horizon), 
            value=max(float(time_horizon), float(st.session_state.res_lifetime[i])), 
            key=f"lifetime_{i}")
    
    st.session_state.res_unit_co2_emission[i] = st.number_input(
        f"Unit CO2 Emission [kgCO2/W]", 
        value=float(st.session_state.res_unit_co2_emission[i]), 
        key=f"co2_{i}")

    if brownfield:
        st.write("##### Brownfield project parameters:")
        st.session_state.res_existing_capacity[i] = st.number_input(
            f"Existing Capacity [kW]", 
            min_value=0.0,
            value=float(st.session_state.res_existing_capacity[i]) * 1000, 
            key=f"exist_cap_{i}") / 1000
        st.session_state.res_existing_years[i] = st.number_input(
            f"Existing Years [years]", 
            min_value=0,
            max_value=(st.session_state.res_lifetime[i] - 1),
            value=float(st.session_state.res_existing_years[i]), 
            key=f"exist_years_{i}")

def solar_pv() -> None:
    """Streamlit page for configuring renewable energy technology parameters."""
    st.title("Solar PV")
    st.subheader("Define the parameters for Solar PV")

    # Initialize session state variables
    initialize_session_state(st.session_state.default_values, 'solar_pv_parameters')
    st.session_state.solar_pv_num_units = st.number_input("Enter the number of units", min_value=1, value=st.session_state.solar_pv_num_units)
    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.installation_dates) != st.session_state.solar_pv_num_units:
        st.session_state.installation_dates = [dt.datetime.now() for _ in range(st.session_state.solar_pv_num_units)]

    st.session_state.selected_timezone_solar_pv = render_timezone_selector()

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
            same_installation_time = st.time_input(
                "Installation Time",
                value=st.session_state.installation_dates[0].time() #if st.session_state.installation_dates[0] else dt.datetime.now().time()
            )
            
            # Combine date and time
            same_installation_datetime = combine_date_and_time(same_installation_date, same_installation_time)
            
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
                input_time = st.time_input(
                    f"Installation Time for Unit {i + 1}",
                    value=st.session_state.installation_dates[i].time() if st.session_state.installation_dates else dt.time.min,
                    key=f"time_input_{i}"
                )
                
                # Combine date and time into a datetime object
                st.session_state.installation_dates[i] = combine_date_and_time(input_date, input_time)
    else:
        # Only one unit, so no checkbox needed
        st.write("Enter the installation date for the unit:")
        input_date = st.date_input(
            "Installation Date",
            value=st.session_state.installation_dates[0].date() if st.session_state.installation_dates else dt.datetime.combine(dt.date.today(), dt.time.min)
        )
        input_time = st.time_input(
            "Installation Time",
            value=st.session_state.installation_dates[0].time() if st.session_state.installation_dates else dt.time.min
        )
        
        # Combine date and time into a datetime object
        st.session_state.installation_dates[0] = combine_date_and_time(input_date, input_time)
    
    st.session_state.installation_dates_utc = convert_dates_to_utc(st.session_state.installation_dates, st.session_state.selected_timezone_solar_pv)

    # Adjust the installation dates list if the number of units changes
    if len(st.session_state.solar_pv_type) != st.session_state.solar_pv_num_units:
        st.session_state.solar_pv_type = [None] * st.session_state.solar_pv_num_units

    if st.session_state.solar_pv_num_units > 1:
        st.write("Enter the number of PV types that were used:")
        # Checkbox to determine if the type is the same for all units
        st.session_state.same_type = st.checkbox("Same type for all units", value=st.session_state.same_type)

        if st.session_state.same_type:
            # Select the same type for all units
            st.session_state.num_solar_pv_types = 1
            st.session_state.solar_pv_types = ['Type 1']  
            for i in range(st.session_state.solar_pv_num_units):
                st.session_state.solar_pv_type[i] = st.session_state.solar_pv_types[0]
        else:
            st.session_state.num_solar_pv_types = st.number_input("Enter the number of types", min_value=2, max_value=st.session_state.num_units, value=max(st.session_state.num_solar_pv_types,2))
            st.session_state.solar_pv_types = [None] * st.session_state.num_solar_pv_types
            for i in range(st.session_state.num_solar_pv_types):
                st.session_state.solar_pv_types[i] = f'Type {i+1}'

            # Multiple select boxes for each unit
            st.write("Select the type for each unit:")

            for i in range(st.session_state.solar_pv_num_units):
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

    st.write("Choose what was included in your calculations:")

    st.session_state.pv_degradation = st.checkbox("Yearly PV degradation", value=st.session_state.pv_degradation)

    st.session_state.pv_temperature_dependent_efficiency = st.checkbox("Temperature dependent PV efficiency", value=st.session_state.pv_temperature_dependent_efficiency)

    st.session_state.pv_dynamic_inverter_efficiency = st.checkbox("Dynamic inverter efficency", value=st.session_state.pv_dynamic_inverter_efficiency)

    for i in range(st.session_state.num_solar_pv_types):
        st.write(f"Enter Solar PV parameters for type {i+1}:")
        
        if len(st.session_state.pv_lifetime) != st.session_state.num_solar_pv_types:
            st.session_state.pv_lifetime = [0] * st.session_state.num_solar_pv_types
        st.session_state.pv_lifetime[i] = st.number_input(f"Type {i+1} PV lifetime (in years):", min_value=0, value=st.session_state.pv_lifetime[i])

        if len(st.session_state.pv_area) != st.session_state.num_solar_pv_types:
            st.session_state.pv_area = [0.0] * st.session_state.num_solar_pv_types
        st.session_state.pv_area[i] = st.number_input(f"Type {i+1} PV area:", min_value=0.0, value=st.session_state.pv_area[i])

        if len(st.session_state.pv_efficiency) != st.session_state.num_solar_pv_types:
            st.session_state.pv_efficiency = [0.0] * st.session_state.num_solar_pv_types
        st.session_state.pv_efficiency[i] = st.number_input(f"Type {i+1} PV efficiency:", min_value=0.0, value=st.session_state.pv_efficiency[i])

        if len(st.session_state.pv_theta_tilt) != st.session_state.num_solar_pv_types:
            st.session_state.pv_theta_tilt = [0.0] * st.session_state.num_solar_pv_types
        st.session_state.pv_theta_tilt[i] = st.number_input(f"Type {i+1} PV tilt angle:", min_value=0.0, value=st.session_state.pv_theta_tilt[i])
        if st.session_state.pv_degradation:
            if len(st.session_state.pv_degradation_rate) != st.session_state.num_solar_pv_types:
                st.session_state.pv_degradation_rate = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_degradation_rate[i] = st.number_input(f"Type {i+1} PV degradation rate:", min_value=0.0, value=st.session_state.pv_degradation_rate[i])
        if st.session_state.pv_temperature_dependent_efficiency:
            if len(st.session_state.pv_temperature_coefficient) != st.session_state.num_solar_pv_types:
                st.session_state.pv_temperature_coefficient = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_temperature_coefficient[i] = st.number_input(f"Type {i+1} PV temperature coefficient:", min_value=0.0, value=st.session_state.pv_temperature_coefficient[i])
            if len(st.session_state.pv_T_ref) != st.session_state.num_solar_pv_types:
                st.session_state.pv_T_ref = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_T_ref[i] = st.number_input(f"Type {i+1} PV refrence Temperature:", min_value=0.0, value=st.session_state.pv_T_ref[i])
            if len(st.session_state.pv_T_ref_NOCT) != st.session_state.num_solar_pv_types:
                st.session_state.pv_T_ref_NOCT = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_T_ref_NOCT[i] = st.number_input(f"Type {i+1} PV NOCT reference temperature:", min_value=0.0, value=st.session_state.pv_T_ref_NOCT[i])
            if len(st.session_state.pv_NOCT) != st.session_state.num_solar_pv_types:
                st.session_state.pv_NOCT = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_NOCT[i] = st.number_input(f"Type {i+1} PV NOCT:", min_value=0.0, value=st.session_state.pv_NOCT[i])
            if len(st.session_state.pv_I_ref_NOCT) != st.session_state.num_solar_pv_types:
                st.session_state.pv_I_ref_NOCT = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_I_ref_NOCT[i] = st.number_input(f"Type {i+1} PV NOCT reference irradiation:", min_value=0.0, value=st.session_state.pv_I_ref_NOCT[i])
        if not st.session_state.pv_dynamic_inverter_efficiency:
            if len(st.session_state.pv_inverter_efficiency) != st.session_state.num_solar_pv_types:
                st.session_state.pv_inverter_efficiency = [0.0] * st.session_state.num_solar_pv_types
            st.session_state.pv_inverter_efficiency[i] = st.number_input(f"Type {i+1} inverter efficiency:", min_value=0.0, value=st.session_state.pv_inverter_efficiency[i])