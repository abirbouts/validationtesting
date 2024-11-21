import streamlit as st
import pandas as pd
from math import radians as rad, sin, cos, acos, degrees
import datetime
import logging
from config.path_manager import PathManager

def with_GHI_DHI(
    theta_tilt: float, 
    GHI: float, 
    DHI: float, 
    rho: float, 
    phi_lat: float, 
    phi_lon: float, 
    days_this_year: int, 
    day_of_year: int, 
    UTC_time: float, 
    albedo: bool) -> float:
    """
    Calculate the total solar irradiance on a tilted surface using Global Horizontal Irradiance (GHI) 
    and Diffuse Horizontal Irradiance (DHI).
    Parameters:
    theta_tilt (float): Tilt angle of the surface in degrees.
    GHI (float): Global Horizontal Irradiance in W/m^2.
    DHI (float): Diffuse Horizontal Irradiance in W/m^2.
    rho (float): Ground reflectance (albedo).
    phi_lat (float): Latitude of the location in degrees.
    phi_lon (float): Longitude of the location in degrees.
    days_this_year (int): Total number of days in the current year.
    day_of_year (int): Day of the year (1-365).
    UTC_time (float): Coordinated Universal Time.
    albedo (bool): Whether to include ground-reflected irradiance.
    Returns:
    float: Total solar irradiance on the tilted surface in W/m^2.
    """

    theta_tilt = rad(theta_tilt)
    phi_lat = rad(phi_lat)
    phi_lon = rad(phi_lon)
    
    B = (360/days_this_year) * (day_of_year-81) # day angle
    B = rad(B)  
    
    delta = 23.45 * sin(B)  # solar declination angle
    delta = rad(delta)
    
    EOT = 9.87 * sin(2 * B) - 7.53 * cos(B) - 1.5 * sin(B)  # equation of time
    
    LST = UTC_time + phi_lon / 15 + EOT / 60  # local solar time
    
    omega = 15 * (LST - 12)  # hour angle
    omega = rad(omega)
    
    # Solar zenith angle (theta_z)
    theta_z = sin(phi_lat) * sin(delta) + cos(phi_lat) * cos(delta) * cos(omega)
    theta_z = acos(theta_z)
    
    # Direct Normal Irradiance (DNI)
    DNI = cos(theta_z) * GHI - DHI
    
    # Azimuth and sun angles
    phi_sun = (sin(delta) * cos(phi_lat) - cos(delta) * sin(phi_lat) * cos(omega)) / sin(theta_z)
    phi_sun = acos(phi_sun)
    
    cos_phi_azimuth = (sin(delta) * cos(phi_lat) - cos(delta) * sin(phi_lat) * cos(omega)) / cos(theta_z)
    cos_phi_azimuth = max(min(cos_phi_azimuth, 1), -1)  # Ensure within [-1, 1] to avoid math domain errors
    
    if omega < 0:
        phi_azimuth = degrees(acos(cos_phi_azimuth)) 
    else:
        phi_azimuth = 360 - degrees(acos(cos_phi_azimuth))  
        
    # Angle of incidence (theta_inc)
    cos_theta_inc = (
        sin(delta) * sin(phi_lat) * cos(theta_tilt) -
        sin(delta) * cos(phi_lat) * sin(theta_tilt) * cos(rad(phi_azimuth) - phi_sun) +
        cos(delta) * cos(phi_lat) * cos(theta_tilt) * cos(omega) +
        cos(delta) * sin(omega) * sin(theta_tilt) * cos(rad(phi_azimuth) - phi_sun)
    )
    cos_theta_inc = max(-1, min(1, cos_theta_inc))  # Clamp to [-1, 1]
    theta_inc = acos(cos_theta_inc)
    
    # Direct beam irradiance (G_b)
    G_b = DNI * cos(theta_inc)
    
    # Diffuse irradiance (G_d)
    G_d = DHI * ((1 + cos(theta_tilt)) / 2)
    
    # Total irradiance
    G_total = G_b + G_d
    
    # Add ground-reflected irradiance if albedo is True
    if albedo:
        G_r = GHI * rho * ((1 - cos(theta_tilt)) / 2)
        G_total += G_r
    
    return G_total


def with_DNI_DHI(
        theta_tilt: float, 
        DNI: float, 
        DHI: float, 
        rho: float, 
        phi_lat: float, 
        phi_lon: float, 
        days_this_year: int, 
        day_of_year: int, 
        UTC_time: float, 
        albedo: float) -> float:
    """
    Calculate the total solar irradiance on a tilted surface using Direct Normal Irradiance (DNI) and Diffuse Horizontal Irradiance (DHI).
    Parameters:
    theta_tilt (float): Tilt angle of the surface in degrees.
    DNI (float): Direct Normal Irradiance in W/m^2.
    DHI (float): Diffuse Horizontal Irradiance in W/m^2.
    rho (float): Ground reflectance (albedo).
    phi_lat (float): Latitude of the location in degrees.
    phi_lon (float): Longitude of the location in degrees.
    days_this_year (int): Total number of days in the current year.
    day_of_year (int): Day of the year (1-365 or 1-366 for leap years).
    UTC_time (float): Coordinated Universal Time (UTC) in hours.
    albedo (float): Albedo value for ground-reflected irradiance.
    Returns:
    float: Total solar irradiance on the tilted surface in W/m^2.
    """
    
    theta_tilt = rad(theta_tilt)  # Convert tilt to radians
    phi_lat = rad(phi_lat)        # Convert latitude to radians
    phi_lon = rad(phi_lon)        # Convert longitude to radians
    
    B = (360 / days_this_year) * (day_of_year - 81)  # day angle in degrees
    B = rad(B)  # Convert day angle to radians
    
    # Solar declination angle (delta) in radians
    delta = rad(23.45 * sin(B))
    
    # Equation of time (EOT) in minutes
    EOT = 9.87 * sin(2 * B) - 7.53 * cos(B) - 1.5 * sin(B)
    
    # Local Solar Time (LST)
    LST = UTC_time + phi_lon / 15 + EOT / 60
    
    # Hour angle (omega) in radians
    omega = rad(15 * (LST - 12))
    
    # Solar zenith angle (theta_z)
    theta_z_cos = sin(phi_lat) * sin(delta) + cos(phi_lat) * cos(delta) * cos(omega)
    theta_z_cos = max(-1, min(1, theta_z_cos))  # Clamp to [-1, 1]
    theta_z = acos(theta_z_cos)
    
    # Azimuth angle of the sun (phi_sun)
    phi_sun = (sin(delta) * cos(phi_lat) - cos(delta) * sin(phi_lat) * cos(omega)) / sin(theta_z)
    phi_sun = max(-1, min(1, phi_sun))  # Clamp to [-1, 1]
    phi_sun = acos(phi_sun)
    
    # Solar azimuth (phi_azimuth)
    cos_phi_azimuth = (sin(delta) * cos(phi_lat) - cos(delta) * sin(phi_lat) * cos(omega)) / cos(theta_z)
    cos_phi_azimuth = max(-1, min(1, cos_phi_azimuth))  # Clamp to [-1, 1]
    
    if omega < 0:
        phi_azimuth = degrees(acos(cos_phi_azimuth))  # Convert to degrees
    else:
        phi_azimuth = 360 - degrees(acos(cos_phi_azimuth))  # Convert to degrees
    
    # Angle of incidence (theta_inc)
    cos_theta_inc = (
        sin(delta) * sin(phi_lat) * cos(theta_tilt) -
        sin(delta) * cos(phi_lat) * sin(theta_tilt) * cos(rad(phi_azimuth) - phi_sun) +
        cos(delta) * cos(phi_lat) * cos(theta_tilt) * cos(omega) +
        cos(delta) * sin(omega) * sin(theta_tilt) * cos(rad(phi_azimuth) - phi_sun)
    )
    cos_theta_inc = max(-1, min(1, cos_theta_inc))  # Clamp to [-1, 1]
    theta_inc = acos(cos_theta_inc)
    
    # Direct beam irradiance (G_b) on the tilted surface
    G_b = DNI * cos(theta_inc)
    
    # Diffuse irradiance (G_d) on the tilted surface
    G_d = DHI * ((1 + cos(theta_tilt)) / 2)
    
    # Total irradiance (G_total) on the tilted surface
    G_total = G_b + G_d
    
    # Add ground-reflected irradiance if albedo is provided
    if albedo:
        G_r = DHI * rho * ((1 - cos(theta_tilt)) / 2)
        G_total += G_r
    
    return G_total
