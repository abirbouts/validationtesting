import streamlit as st
import contextlib
import io
from io import StringIO
import threading
import time
import logging

from pathlib import Path
from datetime import datetime

from validationtesting.model.parameters import ProjectParameters
from validationtesting.model.benchmark import Benchmark
from validationtesting.model.benchmark_validation_testing import ERROR
from validationtesting.model.battery_validation_testing import battery_validation_testing
from config.path_manager import PathManager

# Function to set up logging to both a file and StringIO stream
def setup_logging(log_file_path):
    # Set up StringIO stream to capture logs for the UI
    log_stream = StringIO()

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers, if any
    if logger.hasHandlers():
        logger.handlers.clear()

    # Set up a handler to write logs to the StringIO stream (for real-time UI)
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setLevel(logging.INFO)

    # Set up a handler to write logs to a file (for persistent logging)
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setLevel(logging.INFO)

    # Define a log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return log_stream

def log_window(project_name, log_file_path):
    # Set up logging to a file and capture logs for UI
    log_stream = setup_logging(log_file_path)

    # Placeholder to display logs dynamically in the UI
    log_placeholder = st.empty()

    # Initialize and run the Benchmark class
    benchmark = Benchmark()
    benchmark_result = benchmark.run()

    # Update log display after Benchmark
    log_placeholder.text_area("Logs", value=log_stream.getvalue(), height=300)

    # Initialize and run the Validation_Testing class
    validation_testing = Validation_Testing()
    validation_testing_result = validation_testing.run()

    # Update log display after Validation_Testing
    log_placeholder.text_area("Logs", value=log_stream.getvalue(), height=300)

    # Display the results
    st.success(f"Benchmark Result: {benchmark_result}")
    st.success(f"Validation Testing Result: {validation_testing_result}")

    st.success(f"Logs saved to: {log_file_path}")

def datetime_to_str(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def update_nested_settings(settings):
    for field in settings.model_fields:
        if hasattr(settings, field):
            value = getattr(settings, field)
            if isinstance(value, (int, float, str, bool)):
                if field in st.session_state:
                    setattr(settings, field, st.session_state[field])
            elif isinstance(value, datetime):
                if field in st.session_state:
                    setattr(settings, field, datetime_to_str(st.session_state[field]))
            elif isinstance(value, list):
                if field in st.session_state:
                    new_value = st.session_state[field]
                    if isinstance(new_value, list):
                        setattr(settings, field, new_value)
                    else:
                        setattr(settings, field, [new_value])  # Convert single value to list
            elif isinstance(value, dict):
                if field in st.session_state:
                    new_value = st.session_state[field]
                    if isinstance(new_value, dict):
                        current_dict = getattr(settings, field)
                        current_dict.update(new_value)
                        setattr(settings, field, current_dict)
            elif hasattr(value, 'model_fields'):
                if field == 'renewables_params':
                    setattr(settings, field, update_renewable_params(value, settings.resource_assessment.res_sources))
                elif field == 'generator_params':
                    setattr(settings, field, update_generator_params(value, settings.generator_params.gen_types))
                else:
                    setattr(settings, field, update_nested_settings(value))
    return settings

def update_renewable_params(renewables_params, res_sources):
    renewable_fields = [
        'res_existing_area', 'res_existing_capacity', 'res_existing_years',
        'res_inverter_efficiency', 'res_lifetime', 'res_specific_area',
        'res_specific_investment_cost', 'res_specific_om_cost', 'res_unit_co2_emission']
    
    for field in renewable_fields:
        if hasattr(renewables_params, field):
            current_value = getattr(renewables_params, field)
            if isinstance(current_value, list):
                if field in st.session_state:
                    new_value = st.session_state[field]
                    if isinstance(new_value, list):
                        setattr(renewables_params, field, new_value[:res_sources])
                    else:
                        setattr(renewables_params, field, [new_value] * res_sources)
                else:
                    setattr(renewables_params, field, current_value[:res_sources])

    return renewables_params

def update_generator_params(generator_params, gen_types):
    generator_fields = [
        'fuel_co2_emission', 'fuel_lhv', 'fuel_names', 'gen_cost_increase',
        'gen_existing_capacity', 'gen_existing_years', 'gen_lifetime',
        'gen_min_output', 'gen_names', 'gen_nominal_capacity',
        'gen_nominal_efficiency', 'gen_specific_investment_cost',
        'gen_specific_om_cost', 'gen_unit_co2_emission']
    
    for field in generator_fields:
        if hasattr(generator_params, field):
            current_value = getattr(generator_params, field)
            if isinstance(current_value, list):
                if field in st.session_state:
                    new_value = st.session_state[field]
                    if isinstance(new_value, list):
                        setattr(generator_params, field, new_value[:gen_types])
                    else:
                        setattr(generator_params, field, [new_value] * gen_types)
                else:
                    setattr(generator_params, field, current_value[:gen_types])

    return generator_params

def run_model():
    st.title("Run Validation Testing")
    
    # Get the current project's YAML file path
    project_name: str = st.session_state.get('project_name')
    solver: str = st.session_state.get('solver')
    if not project_name:
        st.error("No project is currently loaded. Please create or load a project first.")
        return

    path_manager: PathManager = PathManager(project_name)
    yaml_filepath: Path = path_manager.PROJECTS_FOLDER_PATH / project_name / f"{project_name}.yaml"
    results_enabled = False
    
    if not yaml_filepath.exists():
        st.error(f"YAML file for project '{project_name}' not found. Please ensure the project is set up correctly.")
        return

    # Load current project parameters
    #current_settings = ProjectParameters.instantiate_from_yaml(yaml_filepath)
    '''
    # Update YAML with current session state
    st.subheader("Update and Save Current Settings")
    st.write("Before running the optimization, you can update and save your current settings to the YAML file.")
    
    if st.button("Update and Save Current Settings"):
        try:
            # Update current_settings with values from session state
            updated_settings = update_nested_settings(current_settings)

            # Save updated settings to YAML
            updated_settings.save_to_yaml(str(yaml_filepath))

            st.success(f"Settings successfully updated and saved to {yaml_filepath}")
        except Exception as e:
            st.error(f"An error occurred while saving settings: {str(e)}")
    
    st.write("---")  # Add a separator
    '''

    st.subheader("Validation Testing")
    st.write("""
    Calculate the Errors
    """)

    # Run model button
    if st.button("Validation Testing"):
        # Reload settings from the updated YAML file
        #settings = ProjectParameters.instantiate_from_yaml(str(yaml_filepath))
        #st.success("Project parameters loaded successfully.")

        # Create a log file path
        log_file_path = path_manager.PROJECTS_FOLDER_PATH / project_name / f"{project_name}_solver_log.txt"


        log_stream = setup_logging(log_file_path)

        # Placeholder to display logs dynamically in the UI
        log_placeholder = st.empty()

        # Initialize and run the Benchmark class
        used_components = []
        if st.session_state.solar_pv:
            Benchmark()
            ERROR()
        if st.session_state.battery:
            battery_validation_testing()

        # Update log display after Benchmark
        log_placeholder.text_area("Logs", value=log_stream.getvalue(), height=300)


    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("Back"):
            st.session_state.page = "Grid Connection"
            st.rerun()
    with col2:
        if st.button("View Results", disabled=not results_enabled):
            st.session_state.page = "Results"
            st.rerun()