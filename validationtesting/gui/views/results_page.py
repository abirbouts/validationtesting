"""
This module contains the functions for displaying the results of the validation testing.
"""

import streamlit as st
import numpy as np
import pandas as pd
from config.path_manager import PathManager
import matplotlib.pyplot as plt
import sys
import calendar

from validationtesting.gui.views.utils import initialize_session_state

import pandas as pd

# Apply FiveThirtyEight style
plt.style.use('fivethirtyeight')
textwidthfraction = 0.7
fontsize = 12 / textwidthfraction
fontsize2 = 10 / textwidthfraction
plt.rcParams.update({
    "text.usetex": True,      
    "font.family": "serif",
    "font.size": fontsize,
    "axes.titlesize": fontsize,
    "axes.labelsize": fontsize,
    "legend.fontsize": fontsize,
    "xtick.labelsize": fontsize2,
    "ytick.labelsize": fontsize2
})

@st.dialog("All Timestamps, where the difference between Model and Benchmark exceeds 10 percent")
def flag_details(df, component) -> None:
    """
    Display the timestamps where the difference between the model and benchmark exceeds a certain threshold.
    """
    flagged_df = df[df['Difference Exceeds 10%']]
    flagged_df = flagged_df.reset_index()[['Time', f'Model {component} Energy Total [Wh]', f'Benchmark {component} Energy Total [Wh]']]
    st.write(flagged_df)

@st.dialog("MAE Details")
def mae_details(df) -> None:
    """
    Display the Mean Absolute Error (MAE) details for the model and benchmark.
    """
    st.write(df)

@st.dialog("All Timestamps, where the power constraints are violated")
def power_constraints_details(df) -> None:
    """
    Display the timestamps where the power constraints are violated.
    """
    if st.session_state.generator_model_output_scope == "Per Unit":
        flagged_df = df[(df[[f"Power Constraints Unit {unit+1}" for unit in range(st.session_state.generator_num_units)]] == False).any(axis=1)]
    else:
        flagged_df = df[df[f"Power Constraints Total"] == False]

    st.write(flagged_df)

@st.dialog("Fuel Consumption Details")
def fuel_consumption_details(fuel_consumption_model, fuel_consumption_benchmark) -> None:
    """
    Display the fuel consumption details for the model and benchmark.
    """
    st.write(f"Model Fuel Consumption: {fuel_consumption_model}")
    st.write(f"Benchmark Fuel Consumption: {fuel_consumption_benchmark}")

@st.dialog("All Timestamps, where the charge power constraints are violated")
def charge_power_constraints_details(df) -> None:
    """
    Display the timestamps where the charge power constraints are violated.
    """
    if st.session_state.battery_model_output_scope == "Per Unit":
        flagged_df = df[(df[[f"Charge Power Constraints Unit {unit+1}" for unit in range(st.session_state.battery_num_units)]] == False).any(axis=1)]
    else:
        flagged_df = df[df[f"Charge Power Constraints Total"] == False]
    st.write(flagged_df)

@st.dialog("All Timestamps, where the state of charge constraints are violated")
def soc_constraints_details(df) -> None:
    """
    Display the timestamps where the state of charge constraints are violated.
    """
    if st.session_state.battery_model_output_scope == "Per Unit":
        flagged_df = df[(df[[f"SoC Constraints Unit {unit+1}" for unit in range(st.session_state.battery_num_units)]] == False).any(axis=1)]
    else:
        flagged_df = df[df[f"SoC Constraints Total"] == False]
    st.write(flagged_df)

def add_lcoe_metric(component: str) -> None:
    """
    Add the Levelized Cost of Energy (LCOE) metric to the results.
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"cost_validation.csv"

    # Load data
    df = pd.read_csv(data_path, index_col='Time', parse_dates=True)

def add_difference_flag(component: str) -> pd.DataFrame:
    """
    Display the number of timestamps where the difference between the model and benchmark exceeds a certain threshold.
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"combined_model_benchmark.csv"

    # Load data
    df = pd.read_csv(data_path, index_col='Time', parse_dates=True)

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
    st.metric(label="Deviation exceeds 10%", value=flag_count)
    if st.button(f"View details", key = f"{component}_flag_count"):
        flag_details(df, component)
    return

def mae_metric(component: str) -> None:
    """
    Display the Mean Absolute Error (MAE) metric for the model and benchmark.
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "Error Calculation" / f"{component}_mae_total.csv"
    df = pd.read_csv(data_path)
    st.metric(label="MAE Total", value=round(df['MAE Total'][0], 2))
    if st.button(f"View details", key=f"{component}_mae_details"):
        mae_details(df)
    return

def power_constraints_metric() -> None:
    """
    Display the number of timestamps where the power constraints are violated.
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"generator_validation.csv"
    df = pd.read_csv(data_path)
    count = 0
    if st.session_state.generator_model_output_scope == "Per Unit":
        for unit in range(st.session_state.generator_num_units):
            count += (df[f"Power Constraints Unit {unit+1}"] == False).sum()
    else:
        count = (df["Power Constraints Total"] == False).sum()
    st.metric(label="Power out of boundary:", value=count)
    if st.button(f"View details", key=f"generator_power_constraints_details"):
        power_constraints_details(df)
    return

def fuel_consumption_metric() -> None:
    """
    Display the fuel consumption difference between the model and benchmark.
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"generator_validation.csv"
    df = pd.read_csv(data_path)
    fuel_consumption_model = 0
    fuel_consumption_benchmark = 0
    if st.session_state.generator_model_output_scope == "Per Unit":
        for unit in range(st.session_state.generator_num_units):
            fuel_consumption_model += st.session_state.generator_total_fuel_consumption[unit]
            fuel_consumption_benchmark += df[f"Benchmark Fuel Consumption generator Unit {unit+1} [l]"].sum()
    else:
        fuel_consumption_model = st.session_state.generator_total_fuel_consumption[0]
        fuel_consumption_benchmark = df["Benchmark Fuel Consumption generator Total [l]"].sum()
    percentage_difference = round((abs(fuel_consumption_model - fuel_consumption_benchmark) / fuel_consumption_benchmark)/100, 3)
    st.metric(label="Fuel Consumption Difference:", value=str(percentage_difference) + "%")
    if st.button(f"View details", key=f"generator_fuel_consumption_details"):
        fuel_consumption_details(fuel_consumption_model, fuel_consumption_benchmark)
    return

def charge_power_constraints_metric() -> None:
    """
    Display the number of timestamps where the charge power constraints are violated.
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"battery_validation.csv"
    df = pd.read_csv(data_path)
    count = 0
    if st.session_state.battery_model_output_scope == "Per Unit":
        for unit in range(st.session_state.generator_num_units):
            count += (df[f"Charge Power Constraints Unit {unit+1}"] == False).sum()
    else:
        count = (df["Charge Power Constraints Total"] == False).sum()
    st.metric(label="Charge power out of boundary:", value=count)
    if st.button(f"View details", key=f"charge_power_constraints_details"):
        charge_power_constraints_details(df)
    return

def soc_constraints_metric() -> None:
    """
    Display the number of timestamps where the state of charge constraints are violated.
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"battery_validation.csv"
    df = pd.read_csv(data_path)
    count = 0
    if st.session_state.battery_model_output_scope == "Per Unit":
        for unit in range(st.session_state.generator_num_units):
            count += (df[f"SoC Constraints Unit {unit+1}"] == False).sum()
    else:
        count = (df["SoC Constraints Total"] == False).sum()
    st.metric(label="State of Charge out of boundary:", value=count)
    if st.button(f"View details", key=f"soc_constraints_details"):
        soc_constraints_details(df)
    return

def plot_model_vs_benchmark(component: str) -> None:
    """
    Generate plot to compare the model and benchmark output for a given component.
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")

    # Define file paths
    data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"combined_model_benchmark.csv"
    plot_folder = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots"

    # Load data
    df = pd.read_csv(data_path, index_col='Time', parse_dates=True)

    # Calculate hourly statistics for the entire year (Daily Pattern)
    if component == "battery":
        hourly_stats_model = df.groupby(df.index.hour)['Model battery SoC Total [%]'].agg(['mean', 'min', 'max'])
        hourly_stats_benchmark = df.groupby(df.index.hour)['Benchmark battery SoC Total [%]'].agg(['mean', 'min', 'max'])

    else:
        hourly_stats_model = df.groupby(df.index.hour)[f'Model {component} Energy Total [Wh]'].agg(['mean', 'min', 'max'])
        hourly_stats_benchmark = df.groupby(df.index.hour)[f'Benchmark {component} Energy Total [Wh]'].agg(['mean', 'min', 'max'])

    # Plot daily pattern
    fig, ax = plt.subplots(figsize=(12, 6))
    hours = hourly_stats_model.index
    ax.plot(hours, hourly_stats_model['mean'], label='Model Output', color='#E57373')
    ax.plot(hours, hourly_stats_benchmark['mean'], label='Benchmark Output', color='#64B5F6')
    ax.fill_between(hours, hourly_stats_model['min'], hourly_stats_model['max'], color='#E57373', alpha=0.3, label='Model Output Range')
    ax.fill_between(hours, hourly_stats_benchmark['min'], hourly_stats_benchmark['max'], color='#64B5F6', alpha=0.3, label='Benchmark Output Range')
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel('Output [Wh]')
    #ax.set_title(f'Daily Average Energy Production')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.grid(True)
    plt.tight_layout()

    # Save daily plot
    daily_plot_path = plot_folder / f"{component}_model_vs_benchmark.png"
    plt.savefig(daily_plot_path, bbox_inches='tight', facecolor="white", edgecolor="white")
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
        ax.plot(hours, hourly_stats_model['mean'], label='Model Output (Average)', color='#E57373')
        ax.plot(hours, hourly_stats_benchmark['mean'], label='Benchmark Output (Average)', color='#64B5F6')
        ax.fill_between(hours, hourly_stats_model['min'], hourly_stats_model['max'], color='#E57373', alpha=0.3, label='Model Output Range (Min to Max)')
        ax.fill_between(hours, hourly_stats_benchmark['min'], hourly_stats_benchmark['max'], color='#64B5F6', alpha=0.3, label='Benchmark Output Range (Min to Max)')
        ax.set_xlabel('Hour of the Day')
        ax.set_ylabel('Output [Wh]')
        ax.set_title(f'Monthly Average Output with Range for {month_name} - {component}')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.grid(True)
        plt.tight_layout()

        # Save monthly plot
        monthly_plot_path = plot_folder / f"{component}_monthly_output_with_range_{month_name}.png"
        plt.savefig(monthly_plot_path, bbox_inches='tight', facecolor="white", edgecolor="white")
        plt.close()

    print(f"Daily and monthly output range plots saved in {plot_folder}.")

def plot_mae(component: str) -> None:
    """
    Generate plot to compare the model and benchmark output for a given component using Mean Absolute Error (MAE).
    """
    # Load project name from session state
    project_name = st.session_state.get("project_name")
    granularities = ["yearly", "monthly", "hourly"]
    scopes = ["Year", "Month", "Hour"]

    for granularity, scope in zip(granularities, scopes):
        # Define file paths
        mae_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "Error Calculation" / f"{component}_mae_{granularity}.csv"
        benchmark_data_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "Error Calculation" / f"{component}_benchmark_mean_{granularity}.csv"
        
        # Load data
        mae_data = pd.read_csv(mae_data_path)
        benchmark_data = pd.read_csv(benchmark_data_path)

        # Merge data on the specified scope (e.g., "Hour", "Month", or "Year")
        merged_data = pd.merge(mae_data, benchmark_data, on=scope, how='outer')

        # Sort by month if the scope is "Month"
        if scope == "Month":
            merged_data[scope] = pd.Categorical(merged_data[scope], categories=list(calendar.month_name)[1:], ordered=True)
            merged_data = merged_data.sort_values(by=scope)

        # Create a new figure
        plt.figure(figsize=(10, 5))
        plt.errorbar(merged_data[scope], merged_data['Mean Benchmark Total'], 
                     yerr=merged_data['MAE Total'], fmt='-o', color='#64B5F6', ecolor='#E57373', 
                     capsize=5, label='Benchmark with MAE')

        plt.xlabel(scope)
        plt.ylabel('Benchmark Output [Wh]')
        plt.title(f'{scope}-wise Benchmark Output with Mean Absolute Error')

        # Add MAE values above error bars
        for i in range(len(merged_data)):
            plt.text(merged_data[scope][i], 
                     merged_data.loc[i, 'Mean Benchmark Total'] + merged_data.loc[i, 'MAE Total'], 
                     f'{merged_data["MAE Total"][i]:.1f}', 
                     ha='center', va='bottom', fontsize=8)
        plt.xticks(rotation=80)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        # Save the plot
        plot_folder = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots"
        plot_path = plot_folder / f"{component}_mae_{granularity}.png"
        plt.savefig(plot_path, bbox_inches='tight', facecolor="white", edgecolor="white")
        plt.close()  # Close the plot to free up memory

def energy_balance_plot() -> None:
    """
    Generate a plot of the average hourly energy balance for a single day.
    """
    import os
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from pathlib import Path

    # Load the data
    project_name = st.session_state.get("project_name")
    result_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / f"energy_balance.csv"
    data = pd.read_csv(result_path)

    # Parse the Time column into datetime and extract the hour
    data['Time'] = pd.to_datetime(data['Time'])
    data['Hour'] = data['Time'].dt.hour
    data.drop(columns=['Total Energy [Wh]'], inplace=True)

    # Extract columns related to energy for renaming and averaging
    energy_columns = data.columns[1:-1]

    # Define a mapping of column names to categories and rename them
    rename_map = {
        col: "Consumption" if "consumption" in col.lower() else
             "Solar PV" if "solar_pv" in col.lower() else
             "Wind" if "wind" in col.lower() else
             "Generator" if "generator" in col.lower() else
             "Battery" if "battery" in col.lower() else col
        for col in energy_columns
    }
    data.rename(columns=rename_map, inplace=True)

    # Define a color map for the categories
    color_map = {
        'Consumption': 'red',
        'Solar PV': 'yellow',
        'Wind': 'blue',
        'Generator': 'grey',
        'Battery': 'green',
    }

    # Ensure numeric data (some columns may have extra whitespace or non-numeric entries)
    for col in rename_map.values():
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')

    # Modify consumption to be negative (from the grid's perspective)
    if "Consumption" in data.columns:
        data['Consumption'] *= -1

    # Group by hour and calculate the average for each energy type
    hourly_avg = data.groupby('Hour')[list(rename_map.values())].mean()

    # Separate positive and negative contributions
    positive_data = hourly_avg.clip(lower=0)
    negative_data = hourly_avg.clip(upper=0)

    # Add the total energy for each hour
    hourly_avg['Total'] = hourly_avg.sum(axis=1)

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))

    # Track which components have been added to the legend
    legend_labels = set()

    # Plot positive contributions (stacked)
    positive_cumulative = np.zeros(len(hourly_avg))
    for col in positive_data.columns:
        if col not in legend_labels:
            ax.bar(hourly_avg.index, positive_data[col], bottom=positive_cumulative, 
                   label=col, color=color_map.get(col, 'grey'))
            legend_labels.add(col)
        else:
            ax.bar(hourly_avg.index, positive_data[col], bottom=positive_cumulative, 
                   color=color_map.get(col, 'grey'))
        positive_cumulative += positive_data[col]

    # Plot negative contributions (stacked downward)
    negative_cumulative = np.zeros(len(hourly_avg))
    for col in negative_data.columns:
        if col not in legend_labels:
            ax.bar(hourly_avg.index, negative_data[col], bottom=negative_cumulative, 
                   label=col, color=color_map.get(col, 'grey'))
            legend_labels.add(col)
        else:
            ax.bar(hourly_avg.index, negative_data[col], bottom=negative_cumulative, 
                   color=color_map.get(col, 'grey'))
        negative_cumulative += negative_data[col]

    # Plot the total as a line
    ax.plot(hourly_avg.index, hourly_avg['Total'], color='black', label='Total (Sum)', linewidth=2)

    # Add labels, legend, and grid
    ax.set_title("Average Hourly Energy Balance (One Day)", fontsize=14)
    ax.set_xlabel("Hour of Day", fontsize=12)
    ax.set_ylabel("Energy (Wh)", fontsize=12)
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax.grid(True, linestyle="--", alpha=0.7)

    # Save the plot
    plt.tight_layout()
    plot_folder = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots"
    os.makedirs(plot_folder, exist_ok=True)
    plot_path = plot_folder / f"energy_balance.png"
    plt.savefig(plot_path, bbox_inches='tight', facecolor="white", edgecolor="white")
    plt.close()

def solar_pv_generate_plots() -> None:
    """
    Generate plots for the solar PV component.
    """
    plot_model_vs_benchmark("solar_pv")
    plot_mae("solar_pv")

def wind_generate_plots() -> None:
    """
    Generate plots for the wind component.
    """
    plot_model_vs_benchmark("wind")
    plot_mae("wind")


def results() -> None:
    """
    Streamlit page for displaying the results of the validation testing.
    """
    st.title("Results")

    initialize_session_state(st.session_state.default_values, 'generate_plots')


    project_name = st.session_state.get("project_name")

    # Dropdown for selecting what should be displayed
    used_components = []
    if st.session_state.energy_balance:
        used_components.append("Energy Balance")
    if st.session_state.solar_pv:
        used_components.append("Solar PV")
    if st.session_state.wind:
        used_components.append("Wind")
    if st.session_state.generator:
        used_components.append("Generator")
    if st.session_state.battery:
        used_components.append("Battery")

    results_component = st.selectbox(
        "Choose for what component you want to see the results:",
        (used_components)
    )

    plots_path = PathManager.PROJECTS_FOLDER_PATH / str(project_name) / "results" / "plots"

    # Show Metrics
    if results_component == "Solar PV":
        col1, col2 = st.columns(2)
        with col1:
            add_difference_flag("solar_pv")
        with col2:
            mae_metric("solar_pv")

    if results_component == "Wind":
        col1, col2 = st.columns(2)
        with col1:
            add_difference_flag("wind")
        with col2:
            mae_metric("wind")

    if results_component == "Generator":
        col1, col2 = st.columns(2)
        with col1:
            power_constraints_metric()
        with col2:
            fuel_consumption_metric()

    if results_component == "Battery":
        col1, col2 = st.columns(2)
        with col1:
            charge_power_constraints_metric()
        with col2:
            soc_constraints_metric()
    
    # Show Plots
    if results_component in ["Solar PV", "Wind", "Energy Balance"]:
        st.subheader("Plots")
        if st.button("Generate Plots"):
            with st.spinner('Generating Plots...'):
                if st.session_state.energy_balance:
                    energy_balance_plot()
                for component in used_components:
                    if component == "Solar PV":
                        function_name = f"solar_pv_generate_plots"
                    else:
                        function_name = f"{component.lower()}_generate_plots"
                    print(f'st.session_state.default_values={st.session_state.default_values}')
                    plot_function = getattr(sys.modules[__name__], function_name, None)
                    plot_function()
                st.session_state.plots_generated = True

        if results_component == "Energy Balance":
            energy_balance_plot_path = plots_path / "energy_balance.png"
            st.image(str(energy_balance_plot_path), caption="Average Hourly Energy Balance", use_container_width=True)

        if results_component == "Solar PV":
            model_vs_benchmark_path = plots_path / f"solar_pv_model_vs_benchmark.png"
            st.image(str(model_vs_benchmark_path), caption=f"Model vs. Benchmark Output", use_container_width=True)
            st.write("Mean Benchmark Output with MAE")
            granularity = st.selectbox("Select Granularity", ["Hourly", "Monthly", "Yearly"])
            mae_path = plots_path / f"solar_pv_mae_{granularity.lower()}.png"
            st.image(str(mae_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_container_width=True)

        if results_component == "Wind":
            model_vs_benchmark_path = plots_path / f"wind_model_vs_benchmark.png"
            st.image(str(model_vs_benchmark_path), caption=f"Model vs. Benchmark Output", use_container_width=True)
            st.write("Mean Benchmark Output with MAE")
            granularity = st.selectbox("Select Granularity", ["Hourly", "Monthly", "Yearly"])
            mae_path = plots_path / f"wind_mae_{granularity.lower()}.png"
            st.image(str(mae_path), caption=f"{granularity} Mean Benchmark Output with MAE", use_container_width=True)
