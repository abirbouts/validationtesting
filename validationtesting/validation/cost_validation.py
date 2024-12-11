import streamlit as st
from datetime import datetime
from dateutil import tz
import pandas as pd
from config.path_manager import PathManager

def get_discounted_cost(start_date, end_date, installation_date, investment_cost, operation_cost, discount_rate, lifetime):
    """
    Calculate the discounted cost of a project given the start date, installation date, investment cost, operation cost, discount rate, lifetime, and salvage value.
    """
    # Calculate the difference in years between the start date and installation date
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.min.time())
    years_diff = (installation_date - start_date).days / 365
    # Initialize the discounted investment cost
    discounted_investment_cost = investment_cost / ((1 + discount_rate) ** years_diff)
    # Calculate the discounted operation cost over the lifetime
    discounted_operation_cost = 0
    for year in range(0, lifetime + 1):
        if installation_date.year + year <= end_date.year:
            discounted_operation_cost += operation_cost / ((1 + discount_rate) ** (year + 1))

    # Calculate the salvage value
    remaining_lifetime = max(0, lifetime - ((end_date - start_date).days / 365))
    salvage_value = investment_cost * (remaining_lifetime / lifetime)
    discounted_salvage_value = salvage_value / ((1 + discount_rate) ** ((end_date - start_date).days / 365))

    return discounted_investment_cost, discounted_operation_cost, discounted_salvage_value

def cost_validation() -> None:

    start_date = st.session_state.start_date
    end_date = st.session_state.end_date
    discount_rate = st.session_state.discount_rate / 100

    used_components = []
    if st.session_state.solar_pv:
        used_components.append("solar_pv")
    if st.session_state.wind:
        used_components.append("wind")
    if st.session_state.generator:
        used_components.append("generator")
    if st.session_state.battery:
        used_components.append("battery")

    economic_validation = pd.DataFrame(columns=["Component", "Unit", "LCOE [$/kWh]", "Discounted Energy [kWh]", "Total Discounted Cost [$]", "Discounted Investment Cost [$]", "Discounted Operation Cost [$]", "Discounted Salvage Value [$]", "Discounted Fuel Cost [$]"])
    project_name = st.session_state.get("project_name")

    if st.session_state.solar_pv:
        total_discounted_investment_cost = 0
        total_discounted_operation_cost = 0
        total_discounted_salvage_value = 0
        for unit in range(st.session_state.solar_pv_num_units):
            installation_date = st.session_state.installation_dates[unit]
            type = st.session_state.solar_pv_type[unit]
            type_int = int(type.replace("Type ", ""))
            investment_cost = st.session_state.solar_pv_investment_cost[type_int-1]
            operation_cost = st.session_state.solar_pv_maintenance_cost[type_int-1]
            lifetime = st.session_state.pv_lifetime[type_int-1]
            discounted_investment_cost, discounted_operation_cost, discounted_salvage_value = get_discounted_cost(start_date, end_date, installation_date, investment_cost, operation_cost, discount_rate, lifetime)
            total_discounted_investment_cost += discounted_investment_cost
            total_discounted_operation_cost += discounted_operation_cost
            total_discounted_salvage_value += discounted_salvage_value
            economic_validation = pd.concat([economic_validation, pd.DataFrame([{
                "Component": "solar_pv", 
                "Unit": unit+1, 
                "Discounted Investment Cost [$]": discounted_investment_cost, 
                "Discounted Operation Cost [$]": discounted_operation_cost,
                "Discounted Salvage Value [$]": discounted_salvage_value
            }])], ignore_index=True)
        economic_validation = pd.concat([economic_validation, pd.DataFrame([{
            "Component": "solar_pv", 
            "Unit": "Total", 
            "Discounted Investment Cost [$]": total_discounted_investment_cost, 
            "Discounted Operation Cost [$]": total_discounted_operation_cost,
            "Discounted Salvage Value [$]": total_discounted_salvage_value
        }])], ignore_index=True)

    if st.session_state.wind:
        total_discounted_investment_cost = 0
        total_discounted_operation_cost = 0
        total_discounted_salvage_value = 0
        for unit in range(st.session_state.wind_num_units):
            installation_date = st.session_state.installation_dates[unit]
            type = st.session_state.wind_type[unit]
            type_int = int(type.replace("Type ", ""))
            investment_cost = st.session_state.wind_investment_cost[type_int-1]
            operation_cost = st.session_state.wind_maintenance_cost[type_int-1]
            lifetime = st.session_state.wind_lifetime[type_int-1]
            discounted_investment_cost, discounted_operation_cost, discounted_salvage_value = get_discounted_cost(start_date, end_date, installation_date, investment_cost, operation_cost, discount_rate, lifetime)
            total_discounted_investment_cost += discounted_investment_cost
            total_discounted_operation_cost += discounted_operation_cost
            total_discounted_salvage_value += discounted_salvage_value
            economic_validation = pd.concat([economic_validation, pd.DataFrame([{
                "Component": "wind", 
                "Unit": unit+1, 
                "Discounted Investment Cost [$]": discounted_investment_cost, 
                "Discounted Operation Cost [$]": discounted_operation_cost,
                "Discounted Salvage Value [$]": discounted_salvage_value
            }])], ignore_index=True)
        economic_validation = pd.concat([economic_validation, pd.DataFrame([{
            "Component": "wind", 
            "Unit": "Total", 
            "Discounted Investment Cost [$]": total_discounted_investment_cost, 
            "Discounted Operation Cost [$]": total_discounted_operation_cost,
            "Discounted Salvage Value [$]": total_discounted_salvage_value
        }])], ignore_index=True)


    if st.session_state.generator:
        total_discounted_investment_cost = 0
        total_discounted_operation_cost = 0
        total_discounted_salvage_value = 0
        for unit in range(st.session_state.generator_num_units):
            installation_date = st.session_state.installation_dates[unit]
            type = st.session_state.generator_type[unit]
            type_int = int(type.replace("Type ", ""))
            investment_cost = st.session_state.generator_investment_cost[type_int-1]
            operation_cost = st.session_state.generator_maintenance_cost[type_int-1]
            lifetime = st.session_state.generator_lifetime[type_int-1]
            discounted_investment_cost, discounted_operation_cost, discounted_salvage_value = get_discounted_cost(start_date, end_date, installation_date, investment_cost, operation_cost, discount_rate, lifetime)
            total_discounted_investment_cost += discounted_investment_cost
            total_discounted_operation_cost += discounted_operation_cost
            total_discounted_salvage_value += discounted_salvage_value
            economic_validation = pd.concat([economic_validation, pd.DataFrame([{
                "Component": "generator", 
                "Unit": unit+1, 
                "Discounted Investment Cost [$]": discounted_investment_cost, 
                "Discounted Operation Cost [$]": discounted_operation_cost,
                "Discounted Salvage Value [$]": discounted_salvage_value
            }])], ignore_index=True)
        economic_validation = pd.concat([economic_validation, pd.DataFrame([{
            "Component": "generator", 
            "Unit": "Total", 
            "Discounted Investment Cost [$]": total_discounted_investment_cost, 
            "Discounted Operation Cost [$]": total_discounted_operation_cost,
            "Discounted Salvage Value [$]": total_discounted_salvage_value
        }])], ignore_index=True)

    if st.session_state.battery:
        total_discounted_investment_cost = 0
        total_discounted_operation_cost = 0
        total_discounted_salvage_value = 0
        for unit in range(st.session_state.battery_num_units):
            installation_date = st.session_state.installation_dates[unit]
            type = st.session_state.battery_type[unit]
            type_int = int(type.replace("Type ", ""))
            investment_cost = st.session_state.battery_investment_cost[type_int-1]
            operation_cost = st.session_state.battery_maintenance_cost[type_int-1]
            lifetime = st.session_state.battery_lifetime[type_int-1]
            discounted_investment_cost, discounted_operation_cost, discounted_salvage_value = get_discounted_cost(start_date, end_date, installation_date, investment_cost, operation_cost, discount_rate, lifetime)
            total_discounted_investment_cost += discounted_investment_cost
            total_discounted_operation_cost += discounted_operation_cost
            total_discounted_salvage_value += discounted_salvage_value
            economic_validation = pd.concat([economic_validation, pd.DataFrame([{
                "Component": "battery", 
                "Unit": unit+1, 
                "Discounted Investment Cost [$]": discounted_investment_cost, 
                "Discounted Operation Cost [$]": discounted_operation_cost,
                "Discounted Salvage Value [$]": discounted_salvage_value
            }])], ignore_index=True)
        economic_validation = pd.concat([economic_validation, pd.DataFrame([{
            "Component": "battery", 
            "Unit": "Total", 
            "Discounted Investment Cost [$]": total_discounted_investment_cost, 
            "Discounted Operation Cost [$]": total_discounted_operation_cost,
            "Discounted Salvage Value [$]": total_discounted_salvage_value
        }])], ignore_index=True)

    if st.session_state.technical_validation and st.session_state.economic_validation:
        for component in used_components:
            data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"{component}_validation.csv"
            energy_df = pd.read_csv(data_path, index_col='UTC Time', parse_dates=True)
            discounted_fuel_cost = 0
            for unit in range(st.session_state[f'{component}_num_units']):
                if component == "solar_pv" or component == "wind":
                    discounted_energy = energy_df[f'Benchmark {component} Discounted Energy Unit {unit+1} [Wh]'].sum()
                else: 
                    discounted_energy = energy_df[f'Model {component} Discounted Energy Unit {unit+1} [Wh]'].sum()
                if component == "generator":
                    discounted_fuel_cost = energy_df[f'Benchmark Discounted Fuel Cost generator Unit {unit+1} [$]'].sum()
                    economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == unit+1), "Discounted Fuel Cost [$]"] = discounted_fuel_cost
                economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == unit+1), "Discounted Energy [kWh]"] = discounted_energy / 1000
                discounted_investment_cost = economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == unit+1), "Discounted Investment Cost [$]"].values[0]
                discounted_operation_cost = economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == unit+1), "Discounted Operation Cost [$]"].values[0]
                discounted_salvage_value = economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == unit+1), "Discounted Salvage Value [$]"].values[0]
                economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == unit+1), "Total Discounted Cost [$]"] = (discounted_investment_cost + discounted_operation_cost - discounted_salvage_value + discounted_fuel_cost)
                if not component == "battery":
                    economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == unit+1), "LCOE [$/kWh]"] = (discounted_investment_cost + discounted_operation_cost - discounted_salvage_value + discounted_fuel_cost) / (discounted_energy/1000)
            if component == "solar_pv" or component == "wind":
                discounted_energy = energy_df[f'Benchmark {component} Discounted Energy Total [Wh]'].sum()
            else:
                discounted_energy = energy_df[f'Model {component} Discounted Energy Total [Wh]'].sum()
                if component == "generator":
                    discounted_fuel_cost = energy_df[f'Benchmark Discounted Fuel Cost generator Total [$]'].sum()
                    economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == 'Total'), "Discounted Fuel Cost [$]"] = discounted_fuel_cost
            economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == "Total"), "Discounted Energy [kWh]"] = discounted_energy / 1000
            discounted_investment_cost = economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == "Total"), "Discounted Investment Cost [$]"].values[0]
            discounted_operation_cost = economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == "Total"), "Discounted Operation Cost [$]"].values[0]
            discounted_salvage_value = economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == "Total"), "Discounted Salvage Value [$]"].values[0]
            discounted_salvage_value = economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == "Total"), "Discounted Salvage Value [$]"].values[0]
            economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == "Total"), "Total Discounted Cost [$]"] = discounted_investment_cost + discounted_operation_cost - discounted_salvage_value + discounted_fuel_cost
            if not component == "battery":
                economic_validation.loc[(economic_validation['Component'] == component) & (economic_validation['Unit'] == "Total"), "LCOE [$/kWh]"] = (discounted_investment_cost + discounted_operation_cost - discounted_salvage_value + discounted_fuel_cost) / (discounted_energy/1000)

    total_discounted_cost = economic_validation.loc[economic_validation['Unit'] == 'Total', 'Total Discounted Cost [$]'].sum()   
    total_discounted_investment_cost = economic_validation.loc[economic_validation['Unit'] == 'Total', 'Discounted Investment Cost [$]'].sum()
    total_discounted_operation_cost = economic_validation.loc[economic_validation['Unit'] == 'Total', 'Discounted Operation Cost [$]'].sum()
    total_discounted_salvage_value = economic_validation.loc[economic_validation['Unit'] == 'Total', 'Discounted Salvage Value [$]'].sum()
    discounted_fuel_cost = economic_validation.loc[economic_validation['Unit'] == 'Total', 'Discounted Fuel Cost [$]'].sum()
    discounted_energy = economic_validation.loc[economic_validation['Unit'] == 'Total', 'Discounted Energy [kWh]'].sum()
    total_lcoe = (total_discounted_investment_cost + total_discounted_operation_cost - total_discounted_salvage_value + discounted_fuel_cost) / discounted_energy 

    economic_validation = pd.concat([economic_validation, pd.DataFrame([{
        "Component": "Total", 
        "Unit": "Total", 
        "LCOE [$/kWh]": total_lcoe,
        "Discounted Energy [kWh]": discounted_energy,
        "Total Discounted Cost [$]": total_discounted_cost,
        "Discounted Investment Cost [$]": total_discounted_investment_cost, 
        "Discounted Operation Cost [$]": total_discounted_operation_cost,
        "Discounted Salvage Value [$]": total_discounted_salvage_value,
        "Discounted Fuel Cost [$]": discounted_fuel_cost
    }])], ignore_index=True) 

    if economic_validation["Discounted Fuel Cost [$]"].isnull().all() or (economic_validation["Discounted Fuel Cost [$]"].fillna(0) == 0).all():
        economic_validation.drop(columns=["Discounted Fuel Cost [$]"], inplace=True)

    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "cost_validation.csv"
    economic_validation.to_csv(data_path, index=False)

    st.write(economic_validation)
