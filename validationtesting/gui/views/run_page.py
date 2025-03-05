"""
This file contains the code for the Run Validation Testing page of the GUI.
The user can run the validation testing for the selected components.
"""

import streamlit as st
from io import StringIO
import logging

from pathlib import Path
from datetime import datetime

from validationtesting.validation.parameters import ProjectParameters
from validationtesting.validation.benchmark import Benchmark
from validationtesting.validation.error_calculation import ERROR
from validationtesting.validation.battery_validation import battery_validation_testing
from validationtesting.validation.generator_validation import generator_validation_testing
from validationtesting.validation.conversion_losses_validation import conversion_losses_validation
from validationtesting.validation.cost_validation import cost_validation
from validationtesting.validation.energy_balance_validation import energy_balance_validation
from config.path_manager import PathManager

def setup_logging(log_file_path: Path) -> StringIO:
    """
    Function to set up logging to both a file and StringIO stream.
    """
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

def datetime_to_str(obj: object) -> str:
    """
    Function to convert a datetime object to a string.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def run_model() -> None:
    """
    Streamlit page to run the validation testing for the selected components.
    """
    st.title("Run Validation Testing")
    
    # Get the current project's YAML file path
    project_name: str = st.session_state.get('project_name')
    if not project_name:
        st.error("No project is currently loaded. Please create or load a project first.")
        return

    path_manager: PathManager = PathManager(project_name)
    yaml_filepath: Path = path_manager.PROJECTS_FOLDER_PATH / project_name / f"{project_name}.yaml"
    
    if not yaml_filepath.exists():
        st.error(f"YAML file for project '{project_name}' not found. Please ensure the project is set up correctly.")
        return

    # Technical Validation
    if st.session_state.technical_validation:
        st.subheader("Technical Validation")
        st.write("""
        Validation Testing:
                
        """)

        # Run technical validation button
        if st.button("Start Technical Validation"):
            with st.spinner('Calculating benchmarks and checking for boundary exceedances...'):
                progress = 0
                progress_bar = st.progress(progress)
                component_text = st.empty()
                
                number_progress_steps = 0
                if st.session_state.solar_pv:
                    number_progress_steps += 1
                if st.session_state.wind:
                    number_progress_steps += 1
                if st.session_state.battery:
                    number_progress_steps += 1
                if st.session_state.generator:
                    number_progress_steps += 1
                if st.session_state.conversion:
                    number_progress_steps += 1
                if st.session_state.energy_balance:
                    number_progress_steps += 1
                progress_step = 1 / number_progress_steps

                # Create a log file path
                start_time = datetime.now()
                # Run technical validation for all components
                if st.session_state.solar_pv or st.session_state.wind:
                    Benchmark(component_text, progress_bar, progress_step, progress)
                    if st.session_state.solar_pv:
                        progress += progress_step
                    if st.session_state.wind:
                        progress += progress_step
                    ERROR()
                if st.session_state.battery:
                    component_text.text("Battery")
                    battery_validation_testing()
                    progress += progress_step
                    progress_bar.progress(progress)
                if st.session_state.generator:
                    component_text.text("Generator")
                    generator_validation_testing()
                    progress += progress_step
                    progress_bar.progress(progress)
                if st.session_state.conversion:
                    component_text.text("Conversion Losses")
                    conversion_losses_validation()
                    progress += progress_step
                    progress_bar.progress(progress)
                
                if st.session_state.energy_balance:
                    component_text.text("Energy Balance")
                    energy_balance_validation()
                    progress += progress_step
                    progress_bar.progress(progress)
                progress_bar.progress(1)
                end_time = datetime.now()
                calculation_time = end_time - start_time
                st.success(f"Technical Validation Complete, Calculation Time = {calculation_time.total_seconds()} seconds")

    # Economic validation
    if st.session_state.economic_validation:
        st.subheader("Economic Validation")
        st.write("""
        Validation Testing:
                
        """)

        # Run technical validation button
        if st.button("Start Economic Validation"):
            with st.spinner('Calculating benchmarks...'):
                # Create a log file path
                start_time = datetime.now()
                cost_validation()
                end_time = datetime.now()
                calculation_time = end_time - start_time
                st.success(f"Economic Validation Complete, Calculation Time = {calculation_time.total_seconds()} seconds")