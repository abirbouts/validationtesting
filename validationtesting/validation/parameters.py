"""
This module defines a set of classes for configuring and managing parameters.
It can be instantiated from and saved to a YAML file for ease of configuration management.
"""

from datetime import datetime

import yaml
from pydantic import BaseModel, ConfigDict


class ProjectInfo(BaseModel):
    """
    Parameters used for project information.

    Attributes:
        project_name (str): The name of the project.
        project_description (str): A brief description of the project.
    """
    project_name: str
    project_description: str

class ComponentSelection(BaseModel):
    """
    Parameters used for component selection.

    Attributes:
        solar_pv (bool): Whether to include solar PV in the project.
        wind (bool): Whether to include wind in the project.
        generator (bool): Whether to include a generator in the project.
        battery (bool): Whether to include a battery in the project.
        technical_validation (bool): Whether to perform technical validation.
        economic_validation (bool): Whether to perform economic validation.
        energy_balance (bool): Whether to perform energy balance validation.
    """
    # Parameters
    solar_pv: bool
    wind: bool
    generator: bool
    battery: bool
    technical_validation: bool
    economic_validation: bool
    energy_balance: bool
    conversion: bool

class GeneralInfo(BaseModel):
    """
    Parameters used for general info.

    Attributes:
        start_date (datetime): The start date of the project.
        end_date (datetime): The end date of the project.
        discount_rate (float): The discount rate for the project.
        lat (float): The latitude of the project.
        lon (float): The longitude of the project.
    """
    # Parameters
    start_date: datetime
    end_date: datetime
    discount_rate: float
    timezone: str
    lat: float
    lon: float
    current_type: str


class SolarPV(BaseModel):
    """
    Parameters used solar pv configuration.

    Attributes:
        solar_pv_num_units (int): Number of solar PV units.
        same_date (bool): Whether all units share the same installation date.
        installation_dates (list): Installation dates for each unit.
        num_solar_pv_types (int): Number of solar PV types.
        same_type (bool): Whether all units share the same type.
        solar_pv_types (list): List of solar PV types.
        solar_pv_type (list): Type of solar PV for each unit.
        pv_rho (float): The reflectance coefficient for solar PV.
        pv_lifetime (list): Lifetime for each solar PV type.
        solar_pv_calculation_type (list): Energy calculation type for each solar PV type.
        pv_area (list): Area for each solar PV type.
        pv_efficiency (list): Efficiency for each solar PV type.
        pv_nominal_power (list): Nominal power for each solar PV type.
        pv_theta_tilt (list): Tilt angle for each solar PV type.
        pv_azimuth (list): Azimuth angle for each solar PV type.
        pv_degradation (bool): Whether to include degradation for solar PV.
        pv_degradation_rate (list): Degradation rate for each solar PV type.
        pv_temperature_dependent_efficiency (bool): Whether temperature-dependent efficiency is included.
        pv_temperature_coefficient (list): Temperature coefficient for each solar PV type.
        pv_T_ref (list): Reference temperature for each solar PV type.
        pv_T_ref_NOCT (list): Reference temperature for NOCT for each solar PV type.
        pv_NOCT (list): NOCT for each solar PV type.
        pv_I_ref_NOCT (list): Reference irradiance for NOCT for each solar PV type.
        pv_dynamic_inverter_efficiency (bool): Whether dynamic inverter efficiency is included.
        pv_inverter_efficiency (list): Inverter efficiency for each solar PV type.
        solar_pv_investment_cost (list): Investment cost for each solar PV type.
        solar_pv_maintenance_cost (list): Maintenance cost for each solar PV type.
        solar_pv_curtailment (list): Wheter curtailment is included for each solar PV type.
    """
    # Parameters
    solar_pv_num_units: int
    same_date: bool
    installation_dates: list
    num_solar_pv_types: int
    same_type: bool
    solar_pv_types: list
    solar_pv_type: list
    pv_rho: float
    pv_lifetime: list
    solar_pv_calculation_type: list
    pv_area: list
    pv_efficiency: list
    pv_nominal_power: list
    pv_theta_tilt: list
    pv_azimuth: list
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
    solar_pv_investment_cost: list
    solar_pv_exclude_investment_cost: list
    solar_pv_maintenance_cost: list
    solar_pv_end_of_project_cost: list
    solar_pv_curtailment: list

class Battery(BaseModel):
    """
    Parameters used for battery configuration.

    Attributes:
        battery_num_units (int): Number of battery units.
        battery_installation_dates (list): Installation dates for each battery unit.
        battery_same_date (bool): Whether all units share the same installation date.
        battery_same_type (bool): Whether all units share the same type.
        battery_types (list): List of battery types.
        battery_type (list): Type of battery for each unit.
        battery_temporal_degradation (bool): Wether temporal degradation is included.
        battery_cyclic_degradation (bool): Whether cyclic degradation is included.
        battery_dynamic_inverter_efficiency (bool): Whether dynamic inverter efficiency is included.
        battery_capacity (list): Capacity for each battery type.
        battery_lifetime (list): Lifetime for each battery type.
        battery_charging_efficiency (list): Charging efficiency for each battery type.
        battery_discharging_efficiency (list): Discharging efficiency for each battery type.
        battery_roundtrip_efficiency (list): Roundtrip efficiency for each battery type.
        battery_initial_soc (list): Initial state of charge for each battery type.
        battery_min_soc (list): Minimum state of charge for each battery type.
        battery_max_soc (list): Maximum state of charge for each battery type.
        battery_max_charge_power (list): Maximum charge power for each battery type.
        battery_max_discharge_power (list): Maximum discharge power for each battery type.
        battery_inverter_efficiency (list): Inverter efficiency for each battery type.
        battery_efficiency_type (str): Efficiency type for the battery.
        battery_inverter_eff_included (list): Whether inverter efficiency is included for each battery type.
        battery_temporal_degradation_rate (list): Temporal degradation rate for each battery type.
        battery_investment_cost (list): Investment cost for each battery type.
        battery_maintenance_cost (list): Maintenance cost for each battery type.
        battery_chemistry (list): Chemistry for each battery type.
        battery_model (list): Model used for cyclic degradation calculation for each battery type.
    """
    # Parameters
    battery_num_units: int
    battery_installation_dates: list
    battery_same_date: bool
    battery_same_type: bool
    num_battery_types: int
    battery_types: list
    battery_type: list
    battery_temporal_degradation: bool
    battery_cyclic_degradation: bool
    battery_dynamic_inverter_efficiency: bool
    battery_capacity: list
    battery_lifetime: list
    battery_charging_efficiency: list
    battery_discharging_efficiency: list
    battery_roundtrip_efficiency: list
    battery_initial_soc: list
    battery_min_soc: list
    battery_max_soc: list
    battery_max_charge_power: list
    battery_max_discharge_power: list
    battery_min_discharge_time: list
    battery_min_charge_time: list
    battery_inverter_efficiency: list
    battery_efficiency_type: str
    battery_inverter_eff_included: list
    battery_temporal_degradation_rate: list
    battery_investment_cost: list
    battery_exclude_investment_cost: list
    battery_maintenance_cost: list
    battery_end_of_project_cost: list
    battery_chemistry: list
    battery_model: list
    battery_degradation_accounting: str

class SolarIrradiation(BaseModel):
    """
    Parameters used for solar irradiation configuration.

    Attributes:
        solar_irradiation_selected_input_type (str): The selected input type for solar irradiation.
        solar_irradiation_delimiter (str): The delimiter for solar irradiation data.
        solar_irradiation_decimal (str): The decimal separator for solar irradiation data.
        solar_irradiation_time_format (str): The time format for solar irradiation data.
        irradiation_data_uploaded (bool): Whether irradiation data has been uploaded.
        Input_GHI (bool): Whether Global Horizontal Irradiance (GHI) data is included.
        Input_DHI (bool): Whether Diffuse Horizontal Irradiance (DHI) data is included.
        Input_DNI (bool): Whether Direct Normal Irradiance (DNI) data is included.
        Input_G_total (bool): Whether total irradiance data is included.
        solar_irradiation_data_source (str): The data source for solar irradiation data.
        albedo (bool): Whether albedo is included.
        albedo_coefficient (float): The albedo coefficient.
    """
    # Parameters
    solar_irradiation_selected_input_type: str
    solar_irradiation_delimiter: str
    solar_irradiation_decimal: str
    solar_irradiation_time_format: str
    irradiation_data_uploaded: bool
    Input_GHI: bool
    Input_DHI: bool
    Input_DNI: bool
    Input_G_total: bool
    solar_irradiation_data_source: str
    albedo: bool
    albedo_coefficient: float

class Wind(BaseModel):
    """
    Parameters used for wind configuration.

    Attributes:
    wind_num_units (int): Number of wind units.
    wind_installation_dates (list): Installation dates for each wind unit.
    wind_same_date (bool): Whether all units share the same installation date.
    wind_types (list): List of wind types.
    wind_type (list): Type of wind for each unit.
    wind_same_type (bool): Whether all units share the same type.
    wind_turbine_type (list): Turbine type for each wind unit.
    wind_lifetime (list): Lifetime for each wind unit.
    wind_rated_power (list): Rated power for each wind unit.
    wind_drivetrain_efficiency (list): Drivetrain efficiency for each wind unit.
    wind_diameter (list): Diameter for each wind unit.
    wind_hub_height (list): Hub height for each wind unit.
    wind_power_curve_uploaded (list): Whether power curve data has been uploaded for each wind unit.
    wind_temporal_degradation (bool): Whether temporal degradation is included for wind.
    wind_temporal_degradation_rate (list): Temporal degradation rate for each wind unit.
    wind_speed_data_uploaded (bool): Whether wind speed data has been uploaded.
    wind_selected_input_type (str): The selected input type for wind speed data.
    wind_Z1 (float): The height of the first wind speed measurement.
    wind_Z0 (float): The height of the second wind speed measurement.
    wind_surface_type (str): The surface type for wind speed data.
    wind_surface_roughness (float): The surface roughness for wind speed data.
    wind_investment_cost (list): Investment cost for each wind unit.
    wind_maintenance_cost (list): Maintenance cost for each wind unit.
    wind_curtailment (list): Whether curtailment is included for each wind unit.
    """
    wind_num_units: int
    wind_installation_dates: list
    wind_same_date: bool
    wind_types: list
    wind_type: list
    num_wind_types: int
    wind_same_type: bool
    wind_turbine_type: list
    wind_lifetime: list
    wind_rated_power: list
    wind_drivetrain_efficiency: list
    wind_diameter: list
    wind_hub_height: list
    wind_power_curve_uploaded: list
    wind_temporal_degradation: bool
    wind_temporal_degradation_rate: list
    wind_speed_data_uploaded: bool
    wind_selected_input_type: str
    wind_Z1: float
    wind_Z0: float
    wind_surface_type: str
    wind_surface_roughness: float
    wind_investment_cost: list
    wind_exclude_investment_cost: list
    wind_maintenance_cost: list
    wind_end_of_project_cost: list
    wind_curtailment: list

class Generator(BaseModel):
    """
    Parameters used for generator configuration.

    Attributes:
    generator_num_units (int): Number of generator units.
    generator_installation_dates (list): Installation dates for each generator unit.
    generator_same_date (bool): Whether all units share the same installation date.
    generator_types (list): List of generator types.
    generator_type (list): Type of generator for each unit.
    generator_same_type (bool): Whether all units share the same type.
    generator_dynamic_efficiency (bool): Whether dynamic efficiency is included for generator.
    generator_temporal_degradation (bool): Whether temporal degradation is included for generator.
    generator_cyclic_degradation (bool): Whether cyclic degradation is included for generator.
    generator_efficiency (list): Efficiency for each generator unit.
    generator_lifetime (list): Lifetime for each generator unit.
    generator_min_power (list): Minimum power for each generator unit.
    generator_max_power (list): Maximum power for each generator unit.
    generator_fuel_lhv (list): Lower heating value for each generator unit.
    generator_temporal_degradation_rate (list): Temporal degradation rate for each generator unit.
    generator_dynamic_efficiency_type (list): Dynamic efficiency type for each generator unit.
    generator_dynamic_efficiency_uploaded (list): Whether dynamic efficiency data has been uploaded for each generator unit.
    generator_efficiency_formula (list): Efficiency formula for each generator unit.
    generator_fuel_consumption_scope (list): Fuel consumption scope for each generator unit.
    generator_total_fuel_consumption (list): Total fuel consumption for each generator unit.
    generator_investment_cost (list): Investment cost for each generator unit.
    generator_maintenance_cost (list): Maintenance cost for each generator unit.
    generator_fuel_price (float): Fuel price for the generator.
    generator_variable_fuel_price (bool): Whether the fuel price is variable.
    generator_variable_fuel_price_uploaded (bool): Whether the fuel price data has been uploaded.
    """
    generator_num_units: int
    generator_installation_dates: list
    generator_same_date: bool
    num_generator_types: int
    generator_types: list
    generator_type: list
    generator_same_type: bool
    generator_dynamic_efficiency: bool
    generator_temporal_degradation: bool
    generator_cyclic_degradation: bool
    generator_efficiency: list
    generator_lifetime: list
    generator_min_power: list
    generator_max_power: list
    generator_fuel_lhv: list
    generator_temporal_degradation_rate: list
    generator_dynamic_efficiency_type: list
    generator_dynamic_efficiency_uploaded: list
    generator_efficiency_formula: list
    generator_fuel_consumption_scope: list
    generator_total_fuel_consumption: list
    generator_investment_cost: list
    generator_exclude_investment_cost: list
    generator_maintenance_cost: list
    generator_end_of_project_cost: list
    generator_fuel_price: float
    generator_variable_fuel_price: bool
    generator_variable_fuel_price_uploaded: bool

class Conversion(BaseModel):
    solar_pv_conversion_efficiency: float
    wind_conversion_efficiency: float
    generator_conversion_efficiency: float
    battery_conversion_efficiency_ac_dc: float
    battery_conversion_efficiency_dc_ac: float
    solar_pv_connection_type: str
    wind_connection_type: str
    conversion_losses_data_uploaded: bool

class UploadModelOutput(BaseModel):
    """
    Parameters used for model output upload configuration.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    solar_pv_data_uploaded: bool
    solar_pv_model_output_scope: str # "Per Unit", "Total"
    battery_data_uploaded: bool
    battery_model_output_scope: str # "Per Unit", "Total"
    wind_data_uploaded: bool
    wind_model_output_scope: str # "Per Unit", "Total"
    generator_data_uploaded: bool
    generator_model_output_scope: str # "Per Unit", "Total"
    wind_data_uploaded: bool
    wind_model_output_scope: str # "Per Unit", "Total"
    consumption_data_uploaded: bool
    consumption_model_output_scope: str

class GeneratePlots(BaseModel):
    """
    Parameters used for generating plots.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    plots_generated: bool 

class ProjectParameters(BaseModel):
    """
    Aggregate class for all project parameters.
    """    
    # Parameters
    project_info: ProjectInfo
    general_info: GeneralInfo
    component_selection: ComponentSelection
    solar_pv_parameters: SolarPV
    solar_irradiation_parameters: SolarIrradiation
    battery_parameters: Battery
    wind_parameters: Wind
    generator_parameters: Generator
    conversion_parameters: Conversion
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
