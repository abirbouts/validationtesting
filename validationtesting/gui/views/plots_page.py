import streamlit as st
import numpy as np
import pandas as pd
from config.path_manager import PathManager
import matplotlib.pyplot as plt
import sys

from validationtesting.gui.views.utils import initialize_session_state

def plot_mae(component):
    # Load project name from session state
    project_name = st.session_state.get("project_name")
    granularities = ["yearly", "monthly", "hourly"]
    scopes = ["Year", "Month", "Hour"]

    for granularity, scope in zip(granularities, scopes):
        # Define file paths
        mae_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"{component}_mae_{granularity}.csv"
        benchmark_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"{component}_benchmark_mean_{granularity}.csv"
        
        # Load data
        mae_data = pd.read_csv(mae_data_path)
        benchmark_data = pd.read_csv(benchmark_data_path)

        # Merge data on the specified scope (e.g., "Hour", "Month", or "Year")
        merged_data = pd.merge(mae_data, benchmark_data, on=scope, how='outer')

        # Set plotting style
        plt.style.use('fivethirtyeight')

        # Create a new figure
        plt.figure(figsize=(10, 5))
        plt.errorbar(merged_data[scope], merged_data['Mean Benchmark Total'], 
                     yerr=merged_data['MAE Total'], fmt='-o', ecolor='green', 
                     capsize=5, label='Benchmark with MAE')

        plt.xlabel(scope)
        plt.ylabel('Benchmark Output')
        plt.title(f'{scope}-wise Benchmark Output with Mean Absolute Error')

        # Add MAE values above error bars
        for i in range(len(merged_data)):
            plt.text(merged_data[scope][i], 
                     merged_data['Mean Benchmark Total'][i] + merged_data['MAE Total'][i], 
                     f'{merged_data["MAE Total"][i]:.1f}', 
                     ha='center', va='bottom', fontsize=8)
        plt.xticks(rotation=80)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        # Save the plot
        plot_folder = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots"
        plot_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots" / f"{component}_mae_{granularity}.png"
        plt.savefig(plot_path)
        plt.close()  # Close the plot to free up memory

def solar_pv_generate_plots():
    plot_mae("solar_pv")

def wind_generate_plots():
    plot_mae("wind")



def generate_plots():
    st.title("Plots")

    initialize_session_state(st.session_state.default_values, 'generate_plots')


    project_name = st.session_state.get("project_name")

    # Dropdown for selecting the method of input
    used_components = []
    if st.session_state.solar_pv:
        used_components.append("Solar PV")
    if st.session_state.wind:
        used_components.append("Wind")
    if st.session_state.generator:
        used_components.append("Generator")
    if st.session_state.battery:
        used_components.append("Battery")


    if st.button("Generate Plots"):
        for component in used_components:
            if component == "Solar PV":
                function_name = f"solar_pv_generate_plots"
            else:
                function_name = f"{component.lower()}_generate_plots"
            print(f'st.session_state.default_values={st.session_state.default_values}')
            plot_function = getattr(sys.modules[__name__], function_name, None)
            plot_function()
        st.session_state.plots_generated = True

    plots_component = st.selectbox(
        "Choose for what component you want to generate/see the plots:",
        (used_components)
    )

    if plots_component == "Solar PV":
        st.write("Mean Benchmark Output with MAE")
        granularity = st.selectbox("Select Granularity", ["Yearly", "Monthly", "Hourly"])
        plot_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots" / f"solar_pv_mae_{granularity.lower()}.png"
        st.image(str(plot_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_column_width=True)

    if plots_component == "Wind":
        st.write("Mean Benchmark Output with MAE")
        granularity = st.selectbox("Select Granularity", ["Yearly", "Monthly", "Hourly"])
        plot_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots" / f"wind_mae_{granularity.lower()}.png"
        st.image(str(plot_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_column_width=True)
