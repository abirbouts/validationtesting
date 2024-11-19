import streamlit as st
import pandas as pd
import numpy as np
from config.path_manager import PathManager
from validationtesting.gui.views.utils import initialize_session_state
import datetime as dt
import logging

class ERROR():
    def __init__(self):
        self.logger = logging.getLogger('MAPE')
        self.logger.info("Starting Error calculation...")
        self.project_name = st.session_state.get("project_name")
        components = {
            "solar_pv",
            "wind"
        }

        combined_data_path = PathManager.PROJECTS_FOLDER_PATH / str(self.project_name) / "results" / f"combined_model_benchmark.csv"
        combined_df = pd.read_csv(combined_data_path)
        combined_df['UTC Time'] = pd.to_datetime(combined_df['UTC Time'])

        benchmark_data = {"total": {}, "yearly": {}, "monthly": {}, "hourly": {}}
        model_data = {"total": {}, "yearly": {}, "monthly": {}, "hourly": {}}
        mae_data = {"total": {}, "yearly": {}, "monthly": {}, "hourly": {}}
        rmse_data = {"total": {}, "yearly": {}, "monthly": {}, "hourly": {}}


        for component_name in components:
            component = st.session_state.get(component_name)
            if component:
                if st.session_state[f'{component_name}_model_output_scope'] == "Per Unit":
                    for i in range (st.session_state[f'{component_name}_num_units']):
                        columns_to_keep = ['UTC Time', f'Model {component_name} Power Unit {i+1}', f'Benchmark {component_name} Power Unit {i+1}']
                        temp_df = combined_df[columns_to_keep]
                        temp_df = temp_df.set_index('UTC Time')
                        temp_df = temp_df.rename(columns={ f'Model {component_name} Power Unit {i+1}': 'model_output', f'Benchmark {component_name} Power Unit {i+1}': 'benchmark_output'})
                        total_mae, yearly_mae, monthly_mae, hourly_mae = self.mae(temp_df)
                        total_rmse, yearly_rmse, monthly_rmse, hourly_rmse = self.rmse(temp_df)
                        
                        benchmark_mean = temp_df['benchmark_output'].mean()
                        yearly_benchmark_series = temp_df.groupby(temp_df.index.year)['benchmark_output'].mean()
                        yearly_benchmark_mean = {str(year): mean for year, mean in yearly_benchmark_series.items()}
                        monthly_benchmark_series = temp_df.groupby(temp_df.index.month)['benchmark_output'].mean()
                        monthly_benchmark_mean = {pd.to_datetime(month, format='%m').strftime('%B'): mean for month, mean in monthly_benchmark_series.items()}
                        hourly_benchmark_series = temp_df.groupby(temp_df.index.hour)['benchmark_output'].mean()
                        hourly_benchmark_mean = {f"{hour:02d}:00": mean for hour, mean in hourly_benchmark_series.items()}
                        benchmark_data["yearly"][f"Year"] = list(yearly_benchmark_mean.keys()) 
                        benchmark_data["monthly"][f"Month"] = list(monthly_benchmark_mean.keys())
                        benchmark_data["hourly"][f"Hour"] = list(hourly_benchmark_mean.keys())
                        benchmark_data["total"][f"Mean Benchmark Unit {i + 1}"] = [benchmark_mean]
                        benchmark_data["yearly"][f"Mean Benchmark Unit {i + 1}"] = list(yearly_benchmark_mean.values())
                        benchmark_data["monthly"][f"Mean Benchmark Unit {i + 1}"] = list(monthly_benchmark_mean.values())
                        benchmark_data["hourly"][f"Mean Benchmark Unit {i + 1}"] = list(hourly_benchmark_mean.values())


                        model_mean = temp_df['model_output'].mean()
                        yearly_model_series = temp_df.groupby(temp_df.index.year)['model_output'].mean()
                        yearly_model_mean = {str(year): mean for year, mean in yearly_model_series.items()}
                        monthly_model_series = temp_df.groupby(temp_df.index.month)['model_output'].mean()
                        monthly_model_mean = {pd.to_datetime(month, format='%m').strftime('%B'): mean for month, mean in monthly_model_series.items()}
                        hourly_model_series = temp_df.groupby(temp_df.index.hour)['model_output'].mean()
                        hourly_model_mean = {str(hour): mean for hour, mean in hourly_model_series.items()}
                        model_data["yearly"][f"Year"] = list(yearly_model_mean.keys()) 
                        model_data["monthly"][f"Month"] = list(monthly_model_mean.keys())
                        model_data["hourly"][f"Hour"] = list(hourly_model_mean.keys())
                        model_data["total"][f"Mean Model Unit {i + 1}"] = [model_mean]
                        model_data["yearly"][f"Mean Model Unit {i + 1}"] = list(yearly_model_mean.values())
                        model_data["monthly"][f"Mean Model Unit {i + 1}"] = list(monthly_model_mean.values())
                        model_data["hourly"][f"Mean Model Unit {i + 1}"] = list(hourly_model_mean.values())
                        
                        mae_data["yearly"][f"Year"] = list(yearly_mae.keys()) 
                        mae_data["monthly"][f"Month"] = list(monthly_mae.keys())
                        mae_data["hourly"][f"Hour"] = list(hourly_mae.keys())

                        mae_data["total"][f"MAE Unit {i + 1}"] = [total_mae["Total MAE"]]
                        mae_data["yearly"][f"MAE Unit {i + 1}"] = list(yearly_mae.values())
                        mae_data["monthly"][f"MAE Unit {i + 1}"] = list(monthly_mae.values())
                        mae_data["hourly"][f"MAE Unit {i + 1}"] = list(hourly_mae.values())

                        rmse_data["yearly"][f"Year"] = list(yearly_rmse.keys()) 
                        rmse_data["monthly"][f"Month"] = list(monthly_rmse.keys())
                        rmse_data["hourly"][f"Hour"] = list(hourly_rmse.keys())

                        rmse_data["total"][f"RMSE Unit {i + 1}"] = [total_rmse["Total RMSE"]]
                        rmse_data["yearly"][f"RMSE Unit {i + 1}"] = list(yearly_rmse.values())
                        rmse_data["monthly"][f"RMSE Unit {i + 1}"] = list(monthly_rmse.values())
                        rmse_data["hourly"][f"RMSE Unit {i + 1}"] = list(hourly_rmse.values())

                
                columns_to_keep = ['UTC Time', f'Model {component_name} Power Total', f'Benchmark {component_name} Power Total']
                temp_df = combined_df[columns_to_keep]
                temp_df = temp_df.set_index('UTC Time')
                temp_df = temp_df.rename(columns={ f'Model {component_name} Power Total': 'model_output', f'Benchmark {component_name} Power Total': 'benchmark_output'})
                total_mae, yearly_mae, monthly_mae, hourly_mae = self.mae(temp_df)
                total_rmse, yearly_rmse, monthly_rmse, hourly_rmse = self.rmse(temp_df)

                benchmark_mean = temp_df['benchmark_output'].mean()
                yearly_benchmark_series = temp_df.groupby(temp_df.index.year)['benchmark_output'].mean()
                yearly_benchmark_mean = {str(year): mean for year, mean in yearly_benchmark_series.items()}
                monthly_benchmark_series = temp_df.groupby(temp_df.index.month)['benchmark_output'].mean()
                monthly_benchmark_mean = {pd.to_datetime(month, format='%m').strftime('%B'): mean for month, mean in monthly_benchmark_series.items()}
                hourly_benchmark_series = temp_df.groupby(temp_df.index.hour)['benchmark_output'].mean()
                hourly_benchmark_mean = {f"{hour:02d}:00": mean for hour, mean in hourly_benchmark_series.items()}
                benchmark_data["yearly"][f"Year"] = list(yearly_benchmark_mean.keys()) 
                benchmark_data["monthly"][f"Month"] = list(monthly_benchmark_mean.keys())
                benchmark_data["hourly"][f"Hour"] = list(hourly_benchmark_mean.keys())
                benchmark_data["total"][f"Mean Benchmark Total"] = [benchmark_mean]
                benchmark_data["yearly"][f"Mean Benchmark Total"] = list(yearly_benchmark_mean.values())
                benchmark_data["monthly"][f"Mean Benchmark Total"] = list(monthly_benchmark_mean.values())
                benchmark_data["hourly"][f"Mean Benchmark Total"] = list(hourly_benchmark_mean.values())

                model_mean = temp_df['model_output'].mean()
                yearly_model_series = temp_df.groupby(temp_df.index.year)['model_output'].mean()
                yearly_model_mean = {str(year): mean for year, mean in yearly_model_series.items()}
                monthly_model_series = temp_df.groupby(temp_df.index.month)['model_output'].mean()
                monthly_model_mean = {pd.to_datetime(month, format='%m').strftime('%B'): mean for month, mean in monthly_model_series.items()}
                hourly_model_series = temp_df.groupby(temp_df.index.hour)['model_output'].mean()
                hourly_model_mean = {str(hour): mean for hour, mean in hourly_model_series.items()}
                model_data["yearly"][f"Year"] = list(yearly_model_mean.keys()) 
                model_data["monthly"][f"Month"] = list(monthly_model_mean.keys())
                model_data["hourly"][f"Hour"] = list(hourly_model_mean.keys())
                model_data["total"][f"Mean Model Total"] = [model_mean]
                model_data["yearly"][f"Mean Model Total"] = list(yearly_model_mean.values())
                model_data["monthly"][f"Mean Model Total"] = list(monthly_model_mean.values())
                model_data["hourly"][f"Mean Model Total"] = list(hourly_model_mean.values())

                mae_data["yearly"][f"Year"] = list(yearly_mae.keys()) 
                mae_data["monthly"][f"Month"] = list(monthly_mae.keys())
                mae_data["hourly"][f"Hour"] = list(hourly_mae.keys())

                mae_data["total"]["MAE Total"] = [total_mae["Total MAE"]]
                mae_data["yearly"]["MAE Total"] = list(yearly_mae.values())
                mae_data["monthly"]["MAE Total"] = list(monthly_mae.values())
                mae_data["hourly"]["MAE Total"] = list(hourly_mae.values())

                rmse_data["yearly"][f"Year"] = list(yearly_rmse.keys()) 
                rmse_data["monthly"][f"Month"] = list(monthly_rmse.keys())
                rmse_data["hourly"][f"Hour"] = list(hourly_rmse.keys())

                rmse_data["total"]["RMSE Total"] = [total_rmse["Total RMSE"]]
                rmse_data["yearly"]["RMSE Total"] = list(yearly_rmse.values())
                rmse_data["monthly"]["RMSE Total"] = list(monthly_rmse.values())
                rmse_data["hourly"]["RMSE Total"] = list(hourly_rmse.values())

                self.save_as_csv(benchmark_data, "Benchmark_Mean", component_name)
                self.save_as_csv(model_data, "Model_Mean", component_name)
                self.save_as_csv(mae_data, "MAE", component_name)
                self.save_as_csv(rmse_data, "RMSE", component_name)

                results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(self.project_name) / "results"
                logging.info(f'The errors for {component_name} on a yearly, monthly and hourly base are saved in {results_data_path}')

    def save_as_csv(self, data, metric_name, component_name):
        results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(self.project_name) / "results"
        for granularity, granularity_data in data.items():
            df = pd.DataFrame(granularity_data)
            df.index.name = granularity.capitalize()
            results_data_path = PathManager.PROJECTS_FOLDER_PATH / str(self.project_name) / "results" / f"{component_name}_{metric_name.lower()}_{granularity}.csv"
            df.to_csv(results_data_path)
    
    def mae(self, df):
        # Total MAE
        total_mae = {"Total MAE": np.mean(np.abs(df['model_output'] - df['benchmark_output']))}

        # Yearly MAE
        yearly_mae_series = df.groupby(df.index.year).apply(lambda x: np.mean(np.abs(x['model_output'] - x['benchmark_output'])))
        yearly_mae = {str(year): mae for year, mae in yearly_mae_series.items()}

        # Monthly MAE
        monthly_mae_series = df.groupby(df.index.month).apply(lambda x: np.mean(np.abs(x['model_output'] - x['benchmark_output'])))
        monthly_mae = {pd.to_datetime(month, format='%m').strftime('%B'): mae for month, mae in monthly_mae_series.items()}

        # Hourly MAE
        hourly_mae_series = df.groupby(df.index.hour).apply(lambda x: np.mean(np.abs(x['model_output'] - x['benchmark_output'])))
        hourly_mae = {f"{hour:02d}:00": mae for hour, mae in hourly_mae_series.items()}

        return total_mae, yearly_mae, monthly_mae, hourly_mae

    def rmse(self, df):
        # Total RMSE
        total_rmse = {"Total RMSE": np.sqrt(np.mean((df['model_output'] - df['benchmark_output']) ** 2))}

        # Yearly RMSE
        yearly_rmse_series = df.groupby(df.index.year).apply(lambda x: np.sqrt(np.mean((x['model_output'] - x['benchmark_output']) ** 2)))
        yearly_rmse = {str(year): rmse for year, rmse in yearly_rmse_series.items()}

        # Monthly RMSE
        monthly_rmse_series = df.groupby(df.index.month).apply(lambda x: np.sqrt(np.mean((x['model_output'] - x['benchmark_output']) ** 2)))
        monthly_rmse = {pd.to_datetime(month, format='%m').strftime('%B'): rmse for month, rmse in monthly_rmse_series.items()}

        # Hourly RMSE
        hourly_rmse_series = df.groupby(df.index.hour).apply(lambda x: np.sqrt(np.mean((x['model_output'] - x['benchmark_output']) ** 2)))
        hourly_rmse = {f"{hour:02d}:00": rmse for hour, rmse in hourly_rmse_series.items()}

        return total_rmse, yearly_rmse, monthly_rmse, hourly_rmse