"""
This module is used to calculate the benchmark of the model output. 
It uses the solar_pv_benchmark and wind_benchmark to calculate the benchmark and save the combined benchmark in a CSV file.
"""

import streamlit as st
import pandas as pd
from config.path_manager import PathManager
import logging

from validationtesting.validation.solar_pv_validation import solar_pv_benchmark
from validationtesting.validation.wind_validation import wind_benchmark

class Benchmark():
    """Class to calculate the benchmark of the model output"""
    def __init__(self) -> None:
        """Initialize the Benchmark class, run functions to calculate the benchmark and save the combined benchmark"""
        self.logger = logging.getLogger('Benchmark')
        self.logger.info("Starting Benchmark calculation...")
        self.project_name = st.session_state.get("project_name")
        components = {
            "solar_pv": solar_pv_benchmark,
            "wind": wind_benchmark
        }

        combined_df = None

        for component_name, benchmark_function in components.items():
            component = st.session_state.get(component_name)
            if component and callable(benchmark_function):
                benchmark_function()
                resource_df = self.create_df(component_name)
                if combined_df is None: 
                    combined_df = resource_df
                else:
                    combined_df = pd.merge(combined_df, resource_df, on="UTC Time", how='outer')
        combined_data_path = PathManager.PROJECTS_FOLDER_PATH / str(self.project_name) / "results" / f"combined_model_benchmark.csv"
        combined_df.to_csv(combined_data_path, index=False)
        self.logger.info(f"Combined Benchmark saved in {combined_data_path}")

    def create_df(self, resource: str) -> pd.DataFrame:
        """Create a dataframe of the model and benchmark data for one resource"""
        benchmark_data_path = PathManager.PROJECTS_FOLDER_PATH / str(self.project_name) / "results" / f"{resource}_validation.csv"
        model_data_path = PathManager.PROJECTS_FOLDER_PATH / str(self.project_name) / "inputs" / f"model_output_{resource}.csv"
        benchmark_df = pd.read_csv(benchmark_data_path)
        model_df = pd.read_csv(model_data_path)
        combined_df = pd.merge(benchmark_df, model_df, on="UTC Time", how='outer')
        combined_df = combined_df.loc[:, combined_df.columns.str.contains('UTC Time|Model|Benchmark')]
        return combined_df
