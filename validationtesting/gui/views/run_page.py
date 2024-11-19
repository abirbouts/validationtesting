import streamlit as st
import contextlib
import io
from io import StringIO
import threading
import time
import logging

from pathlib import Path
from datetime import datetime

from validationtesting.validation.parameters import ProjectParameters
from validationtesting.validation.benchmark import Benchmark
from validationtesting.validation.benchmark_validation_testing import ERROR
from validationtesting.validation.battery_validation_testing import battery_validation_testing
from validationtesting.validation.generator_validation_testing import generator_validation_testing
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

def datetime_to_str(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


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


    st.subheader("Validation Testing")
    st.write("""
    Validation Testing:
             
    """)

    # Run model button
    if st.button("Validation Testing"):
        # Create a log file path
        log_file_path = path_manager.PROJECTS_FOLDER_PATH / project_name / f"{project_name}_solver_log.txt"

        log_stream = setup_logging(log_file_path)

        # Placeholder to display logs dynamically in the UI
        log_placeholder = st.empty()

        # Initialize and run the Benchmark class
        if st.session_state.solar_pv or st.session_state.wind:
            Benchmark()
            ERROR()
        if st.session_state.battery:
            battery_validation_testing()
        if st.session_state.generator:
            generator_validation_testing()

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