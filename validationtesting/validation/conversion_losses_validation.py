import streamlit as st
from config.path_manager import PathManager
import pandas as pd


def conversion_losses_validation() -> None:

    st.write("--------------------")
    progress_steps = 1
    conversion_progress = 0
    conversion_progress_bar = st.progress(conversion_progress)
    conversion_text = st.empty()

    used_components = []
    if st.session_state.solar_pv and st.session_state.solar_pv_connection_type == "Connected with a seperate Inverter to the Microgrid":
        used_components.append("solar_pv")
        progress_steps += 1
    if st.session_state.wind and st.session_state.wind_connection_type == "Connected with a AC-AC Converter to the Microgrid":
        used_components.append("wind")
        progress_steps += 1
    if st.session_state.generator and st.session_state.current_type == "Direct Current":
        used_components.append("generator")
        progress_steps += 1
    if st.session_state.battery:
        if st.session_state.solar_pv and st.session_state.solar_pv_connection_type == "Connected with the same Inverter as the Battery to the Microgrid":
            used_components.append("DC System")
        else:
            used_components.append("battery")
        progress_steps += 1

    progress_step = 1.0 / progress_steps

    project_name = st.session_state.get("project_name")
    project_folder_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_conversion_losses.csv"
    losses_df = pd.read_csv(project_folder_path)

    result_df = pd.DataFrame()

    for component in used_components:
        conversion_text.write(f"Calculating conversion losses for {component}")
        if not component == "DC System" and not component == "battery":
            component_energy_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_{component}.csv"
            energy_df = pd.read_csv(component_energy_path)
            energy = energy_df[f"Model {component} Energy Total [Wh]"]
            if f"Model {component} Curtailed Energy Total [Wh]" in solar_pv_energy_df.columns:

                st.write("Curtailed Energy Total [Wh] found for", component)
                energy -= energy_df[f"Model {component} Curtailed Energy Total [Wh]"]
            losses = losses_df[f'{component} Conversion Losses [Wh]']
            benchmark_losses = (1-(st.session_state[f"{component}_conversion_efficiency"]/100)) * energy
            component_result_df = pd.DataFrame({
                "Time": energy_df["Time"],
                f"{component} Conversion Losses [Wh]": losses,
                f"{component} Benchmark Losses [Wh]": benchmark_losses
            })
            if result_df.empty:
                result_df = component_result_df
            else:
                result_df = result_df.merge(component_result_df, on="Time", how="outer")
        elif component == "DC System":
            solar_pv_energy_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_solar_pv.csv"
            battery_energy_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_battery.csv"
            solar_pv_energy_df = pd.read_csv(solar_pv_energy_path)
            battery_energy_df = pd.read_csv(battery_energy_path)
            solar_pv_energy = solar_pv_energy_df["Model solar_pv Energy Total [Wh]"]
            if "Model solar_pv Curtailed Energy Total [Wh]" in solar_pv_energy_df.columns:
                solar_pv_energy -= solar_pv_energy_df["Model solar_pv Curtailed Energy Total [Wh]"]
            battery_energy = battery_energy_df["Model battery Energy Total [Wh]"]
            system_energy = solar_pv_energy + battery_energy
            losses = losses_df["DC System Conversion Losses [Wh]"]
            benchmark_losses = pd.Series([
                (1 - (st.session_state["battery_conversion_efficiency_dc_ac"]/100)) * energy if energy > 0 else ((1 / (st.session_state["battery_conversion_efficiency_ac_dc"]/100)) - 1) * abs(energy)
                for energy in system_energy
            ])
            component_result_df = pd.DataFrame({
                "Time": solar_pv_energy_df["Time"],
                "DC System Conversion Losses [Wh]": losses,
                "DC System Benchmark Losses [Wh]": benchmark_losses
            })
            if result_df.empty:
                result_df = component_result_df
            else:
                result_df = result_df.merge(component_result_df, on="Time", how="outer")
        elif component == "battery":
            battery_energy_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "inputs" / f"model_output_battery.csv"
            battery_energy_df = pd.read_csv(battery_energy_path)
            battery_energy = battery_energy_df["Model battery Energy Total [Wh]"]
            losses = losses_df["Battery Conversion Losses [Wh]"]
            benchmark_losses = pd.Series([
                (1 - (st.session_state["battery_conversion_efficiency_dc_ac"]/100)) * energy if energy > 0 else ((1 / (st.session_state["battery_conversion_efficiency_ac_dc"]/100)) - 1) * abs(energy)
                for energy in battery_energy
            ])
            component_result_df = pd.DataFrame({
                "Time": battery_energy_df["Time"],
                "Battery Conversion Losses [Wh]": losses,
                "Battery Benchmark Losses [Wh]": benchmark_losses
            })
            if result_df.empty:
                result_df = component_result_df
            else:
                result_df = result_df.merge(component_result_df, on="Time", how="outer")
        conversion_progress += progress_step
        conversion_progress_bar.progress(conversion_progress)

    conversion_text.write("Saving Solar PV Benchmark Results")   
    results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "conversion_losses_validation.csv"
    result_df.to_csv(results_data_path)
    conversion_text.write("Conversion Losses Benchmark Calculation Completed.")
    conversion_progress += progress_step
    conversion_progress_bar.progress(conversion_progress)