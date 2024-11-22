import streamlit as st
import numpy as np
import pandas as pd
from config.path_manager import PathManager
import matplotlib.pyplot as plt
import sys
import calendar

from validationtesting.gui.views.utils import initialize_session_state

import pandas as pd

@st.dialog("All Timestamps, where the difference between Model and Benchmark exceeds 10 percent")
def flag_details(df) -> None:
    flagged_df = df[df['Difference Exceeds 10%']]
    flagged_df.drop(columns=['Difference Exceeds 10%'], inplace=True)
    st.write(flagged_df)

@st.dialog("MAE Details")
def mae_details(df) -> None:
    st.write(df)

def add_difference_flag(component: str) -> pd.DataFrame:
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"combined_model_benchmark.csv"

    # Load data
    df = pd.read_csv(data_path, index_col='UTC Time', parse_dates=True)

    # Define the model and benchmark columns
    model_col = f'Model {component} Energy Total [Wh]'
    benchmark_col = f'Benchmark {component} Energy Total [Wh]'

    if model_col not in df.columns or benchmark_col not in df.columns:
        raise ValueError(f"Required columns for {component} are not in the dataset.")

    # Calculate the percentage difference and add a new column
    df['Difference Exceeds 10%'] = abs(df[model_col] - df[benchmark_col]) > (0.10 * df[benchmark_col])

    # Save the updated DataFrame back to the file
    updated_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"combined_model_benchmark_with_flag.csv"
    df.to_csv(updated_data_path)
    flag_count = df['Difference Exceeds 10%'].sum()
    st.metric(label="Flag Count", value=flag_count)
    if st.button(f"View details", key = f"{component}_flag_count"):
        flag_details(df)
    return

def mae_metric(component: str) -> None:
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"{component}_mae_total.csv"
    df = pd.read_csv(data_path)
    st.metric(label="MAE Total", value=round(df['MAE Total'][0], 2))
    if st.button(f"View details", key=f"{component}_mae_details"):
        mae_details(df)
    return

def plot_model_vs_benchmark(component: str) -> None:
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"combined_model_benchmark.csv"
    plot_folder = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots"

    # Load data
    df = pd.read_csv(data_path, index_col='UTC Time', parse_dates=True)

    # Use FiveThirtyEight style
    plt.style.use('fivethirtyeight')

    # Calculate hourly statistics for the entire year (Daily Pattern)
    hourly_stats_model = df.groupby(df.index.hour)[f'Model {component} Energy Total [Wh]'].agg(['mean', 'min', 'max'])
    hourly_stats_benchmark = df.groupby(df.index.hour)[f'Benchmark {component} Energy Total [Wh]'].agg(['mean', 'min', 'max'])

    # Plot daily pattern
    fig, ax = plt.subplots(figsize=(12, 6))
    hours = hourly_stats_model.index
    ax.plot(hours, hourly_stats_model['mean'], label='Model Output (Average)', color='red')
    ax.plot(hours, hourly_stats_benchmark['mean'], label='Benchmark Output (Average)', color='blue')
    ax.fill_between(hours, hourly_stats_model['min'], hourly_stats_model['max'], color='lightpink', alpha=0.3, label='Model Output Range (Min to Max)')
    ax.fill_between(hours, hourly_stats_benchmark['min'], hourly_stats_benchmark['max'], color='lightblue', alpha=0.3, label='Benchmark Output Range (Min to Max)')
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Output [Wh]')
    ax.set_title(f'Daily Average Output with Range - {component}')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid(True)
    plt.tight_layout()

    # Save daily plot
    daily_plot_path = plot_folder / f"{component}_model_vs_benchmark.png"
    plt.savefig(daily_plot_path)
    plt.close()

    # Calculate monthly hourly statistics
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        monthly_data = df[df.index.month == month]
        hourly_stats_model = monthly_data.groupby(monthly_data.index.hour)[f'Model {component} Energy Total [Wh]'].agg(['mean', 'min', 'max'])
        hourly_stats_benchmark = monthly_data.groupby(monthly_data.index.hour)[f'Benchmark {component} Energy Total [Wh]'].agg(['mean', 'min', 'max'])

        # Plot monthly pattern
        fig, ax = plt.subplots(figsize=(12, 6))
        hours = hourly_stats_model.index
        ax.plot(hours, hourly_stats_model['mean'], label='Model Output (Average)', color='red')
        ax.plot(hours, hourly_stats_benchmark['mean'], label='Benchmark Output (Average)', color='blue')
        ax.fill_between(hours, hourly_stats_model['min'], hourly_stats_model['max'], color='lightpink', alpha=0.3, label='Model Output Range (Min to Max)')
        ax.fill_between(hours, hourly_stats_benchmark['min'], hourly_stats_benchmark['max'], color='lightblue', alpha=0.3, label='Benchmark Output Range (Min to Max)')
        ax.set_xlabel('Hour of the Day')
        ax.set_ylabel('Output [Wh]')
        ax.set_title(f'Monthly Average Output with Range for {month_name} - {component}')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)
        plt.tight_layout()

        # Save monthly plot
        monthly_plot_path = plot_folder / f"{component}_monthly_output_with_range_{month_name}.png"
        plt.savefig(monthly_plot_path)
        plt.close()

    print(f"Daily and monthly output range plots saved in {plot_folder}.")

def plot_mae(component: str) -> None:
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
        plt.ylabel('Benchmark Output [Wh]')
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

def solar_pv_generate_plots() -> None:
    plot_mae("solar_pv")

def wind_generate_plots() -> None:
    plot_model_vs_benchmark("wind")
    plot_mae("wind")



def results() -> None:
    st.title("Results")

    initialize_session_state(st.session_state.default_values, 'generate_plots')


    project_name = st.session_state.get("project_name")

    # Dropdown for selecting the method of input
    used_components = []
    if st.session_state.solar_pv:
        used_components.append("Solar PV")
    if st.session_state.wind:
        used_components.append("Wind")
    #if st.session_state.generator:
    #    used_components.append("Generator")
    if st.session_state.battery:
        used_components.append("Battery")

    results_component = st.selectbox(
        "Choose for what component you want to see the results:",
        (used_components)
    )

    plots_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots"

    if results_component == "Solar PV":
        model_vs_benchmark_path = plots_path / f"solar_pv_model_vs_benchmark.png"
        st.image(str(model_vs_benchmark_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_column_width=True)
        st.write("Mean Benchmark Output with MAE")
        granularity = st.selectbox("Select Granularity", ["Yearly", "Monthly", "Hourly"])
        mae_path = plots_path / f"solar_pv_mae_{granularity.lower()}.png"
        st.image(str(mae_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_container_width=True)

    if results_component == "Wind":
        col1, col2 = st.columns(2)
        with col1:
            add_difference_flag("wind")
        with col2:
            mae_metric("wind")

    st.subheader("Plots")
    if st.button("Generate Plots"):
        with st.spinner('Generating Plots...'):
            for component in used_components:
                if component == "Solar PV":
                    function_name = f"solar_pv_generate_plots"
                else:
                    function_name = f"{component.lower()}_generate_plots"
                print(f'st.session_state.default_values={st.session_state.default_values}')
                plot_function = getattr(sys.modules[__name__], function_name, None)
                plot_function()
            st.session_state.plots_generated = True

    if results_component == "Solar PV":
        model_vs_benchmark_path = plots_path / f"solar_pv_model_vs_benchmark.png"
        st.image(str(model_vs_benchmark_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_column_width=True)
        st.write("Mean Benchmark Output with MAE")
        granularity = st.selectbox("Select Granularity", ["Yearly", "Monthly", "Hourly"])
        mae_path = plots_path / f"solar_pv_mae_{granularity.lower()}.png"
        st.image(str(mae_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_container_width=True)

    if results_component == "Wind":
        model_vs_benchmark_path = plots_path / f"wind_model_vs_benchmark.png"
        st.image(str(model_vs_benchmark_path), caption=f"Model vs. Benchmark Output with MAE", use_container_width=True)
        st.write("Mean Benchmark Output with MAE")
        granularity = st.selectbox("Select Granularity", ["Hourly", "Monthly", "Yearly"])
        mae_path = plots_path / f"wind_mae_{granularity.lower()}.png"
        st.image(str(mae_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_container_width=True)
