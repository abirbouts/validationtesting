"""
This module defines a set of classes for configuring and managing parameters.
It includes models for project  information, settings, advanced configurations, 
resource assessments, archetype parameters, and renewable energy sources. 
These models are built using Pydantic  for data validation and can be instantiated 
from YAML file or saved to it for ease of configuration management.
"""

from datetime import datetime
from typing import List, Optional
import pandas as pd

import yaml
from pydantic import BaseModel, ConfigDict


class ProjectInfo(BaseModel):
    """
    Model representing project information.

    Attributes:
        project_name (str): The name of the project.
        project_description (str): A brief description of the project.
    """
    project_name: str
    project_description: str

class ComponentSelection(BaseModel):
    """
    Model representing project information.

    Attributes:
        project_name (str): The name of the project.
        project_description (str): A brief description of the project.
    """
    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Parameters
    solar_pv: bool
    wind: bool
    generator: bool
    battery: bool

class ProjectInfo(BaseModel):
    """
    Model representing project information.

    Attributes:
        project_name (str): The name of the project.
        project_description (str): A brief description of the project.
    """
    project_name: str
    project_description: str

class GeneralInfo(BaseModel):
    """
    Model representing project information.

    Attributes:
        project_name (str): The name of the project.
        project_description (str): A brief description of the project.
    """
    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Parameters
    start_date: datetime
    end_date: datetime
    location: str
    lat: float
    lon: float


class SolarPV(BaseModel):
    """
    Model representing project information.

    Attributes:
        project_name (str): The name of the project.
        project_description (str): A brief description of the project.
    """
    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Parameters
    solar_pv_num_units: int
    same_date: bool
    selected_timezone_solar_pv: str
    installation_dates: list
    installation_dates_utc: list
    num_solar_pv_types: int
    same_type: bool
    solar_pv_types: list
    solar_pv_type: list
    pv_lifetime: list
    pv_area: list
    pv_efficiency: list
    pv_theta_tilt: list
    pv_degradation: bool
    pv_degradation_rate: list
    pv_temperature_dependent_efficiency: bool
    pv_temperature_coefficient: list
    pv_T_ref: list
    pv_T_ref_NOCT: list
    pv_NOCT: list
    pv_I_ref_NOCT: list
    pv_dynamic_inverter_efficiency: bool
    pv_inverter_efficiency: list

class Battery(BaseModel):
    """
    Model representing battery parameters.

    Attributes:
        battery_num_units (int): Number of battery units.
        battery_installation_dates (list): Installation dates for each unit.
        battery_installation_dates_utc (list): Installation dates in UTC.
        battery_same_date (bool): Whether all units share the same installation date.
        selected_timezone_battery (str): Selected timezone for battery installation dates.
        battery_types (list): List of battery types.
        battery_type (list): Type of battery for each unit.
        battery_temporal_degradation (bool): Indicates temporal degradation for batteries.
        battery_cyclic_degradation (bool): Indicates cyclic degradation for batteries.
        battery_dynamic_inverter_efficiency (bool): Dynamic inverter efficiency toggle.
        battery_capacity (list): Capacity for each battery type.
        battery_lifetime (list): Lifetime for each battery type.
        battery_charging_efficiency (list): Charging efficiency for each battery type.
        battery_discharging_efficiency (list): Discharging efficiency for each battery type.
        battery_initial_soc (list): Initial state of charge for each battery type.
        battery_min_soc (list): Minimum state of charge for each battery type.
        battery_max_soc (list): Maximum state of charge for each battery type.
        battery_min_charge_power (list): Minimum charging power for each battery type.
        battery_max_charge_power (list): Maximum charging power for each battery type.
        battery_inverter_efficiency (list): Inverter efficiency for each battery type.
    """
    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Parameters
    battery_num_units: int
    battery_installation_dates: list
    battery_installation_dates_utc: list
    battery_same_date: bool
    selected_timezone_battery: str
    battery_same_type: bool
    battery_types: list
    battery_type: list
    battery_temporal_degradation: bool
    battery_cyclic_degradation: bool
    battery_dynamic_inverter_efficiency: bool
    battery_capacity: list
    battery_lifetime: list
    battery_charging_efficiency: list
    battery_discharging_efficiency: list
    battery_initial_soc: list
    battery_min_soc: list
    battery_max_soc: list
    battery_max_charge_power: list
    battery_max_discharge_power: list
    battery_inverter_efficiency: list

class SolarIrradiation(BaseModel):
    """
    Model representing project information.

    Attributes:
        project_name (str): The name of the project.
        project_description (str): A brief description of the project.
    """
    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Parameters
    solar_irradiation_selected_input_type: str
    solar_irradiation_delimiter: str
    solar_irradiation_decimal: str
    solar_irradiation_time_format: str
    solar_irradiation_timezone: str
    irradiation_data_uploaded: bool
    Input_GHI: bool
    Input_DHI: bool
    Input_DNI: bool
    Input_G_total: bool
    solar_irradiation_data_source: str
    albedo: bool
    albedo_coefficient: float
    selected_timezone_solar_irradiation: str


class UploadModelOutput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    solar_pv_data_uploaded: bool
    solar_pv_model_output_scope: str # "Per Unit", "Total"
    battery_data_uploaded: bool
    battery_model_output_scope: str # "Per Unit", "Total"

class GeneratePlots(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    plots_generated: bool 

class ProjectParameters(BaseModel):
    """
    Model representing the default values for the project.

    Attributes:
        project_info (ProjectInfo): The project information.
        project_settings (ProjectSettings): The project settings.
        advanced_settings (AdvancedSettings): The advanced settings.
        nasa_power_params (NasaPowerParams): The NASA POWER API parameters.
        resource_assessment (ResourceAssessment): The resource assessment parameters.
        archetypes_params (ArchetypesParams): The archetype parameters.
        renewables_params (RenewablesParams): The renewable energy source parameters.
        grid_params (GridParams): The grid connection parameters.
    """
    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)
        
    # Parameters
    project_info: ProjectInfo
    general_info: GeneralInfo
    component_selection: ComponentSelection
    solar_pv_parameters: SolarPV
    solar_irradiation_parameters: SolarIrradiation
    battery_parameters: Battery
    upload_model_parameters: UploadModelOutput
    generate_plots: GeneratePlots


    @classmethod
    def instantiate_from_yaml(cls, filepath: str) -> 'ProjectParameters':
        """Instantiate a ProjectParameters object loading parameters from a YAML file."""
        with open(filepath, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return cls(**data)
    
    def save_to_yaml(self, filepath: str) -> None:
        """Save parameters to a YAML file."""
        with open(filepath, 'w') as file:
            yaml.dump(self.model_dump(), file)
