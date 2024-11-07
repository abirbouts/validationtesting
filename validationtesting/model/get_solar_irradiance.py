import streamlit as st
import pandas as pd
from math import radians as rad, sin, cos, acos, degrees
import datetime
import logging
from config.path_manager import PathManager

def with_GHI_DHI(theta_tilt, GHI, DHI, rho, phi_lat, phi_lon, days_this_year, day_of_year, UTC_time, albedo):

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


def with_DNI_DHI(theta_tilt, DNI, DHI, rho, phi_lat, phi_lon, days_this_year, day_of_year, UTC_time, albedo):
    
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

def with_GHI(theta_tilt, H_day, rho, phi_lat, phi_lon, days_this_year, day_of_year, UTC_time, standard_lon, azimuth, albedo):
    
    theta_tilt = rad(theta_tilt)  # Convert tilt to radians
    phi_lat = rad(phi_lat)        # Convert latitude to radians
    phi_lon = rad(phi_lon)        # Convert longitude to radians
    azimuth = rad(azimuth)        # Convert azimuth to radians
    
    B = (360 / days_this_year) * (day_of_year - 81)  # day angle in degrees
    B = rad(B)  # Convert day angle to radians
    
    # Solar declination angle (delta) in radians
    delta = rad(23.45 * sin(B))
    
    # Equation of time (EOT) in minutes
    EOT = 9.87 * sin(2 * B) - 7.53 * cos(B) - 1.5 * sin(B)
    
    # Extraterrestrial irradiation (H_extra)
    E_0 = 1.000110 + 0.034221 * cos(B) + 0.001280 * sin(B) + 0.000719 * cos(2 * B) + 0.000077 * sin(2 * B)
    G_0n = 1.367 * E_0  # Extraterrestrial irradiance in kW/m²
    omega_s = acos(-tan(phi_lat) * tan(delta))  # Sunset hour angle
    H_extra = (24 / pi) * G_0n * (cos(phi_lat) * cos(delta) * sin(omega_s) + omega_s * sin(phi_lat) * sin(delta))
    
    # Calculate the clearness index (K_T)
    K_T = H_day / H_extra
    
    # Estimate diffuse horizontal irradiation (H_diff) using Erbs correlation
    if K_T <= 0.22:
        K_diff = 1 - 0.09 * K_T
    elif 0.22 < K_T <= 0.8:
        K_diff = 0.9511 - 0.1604 * K_T + 4.388 * K_T**2 - 16.638 * K_T**3 + 12.336 * K_T**4
    else:
        K_diff = 0.165
    
    H_diff = K_diff * H_day  # Daily diffuse irradiation on the surface

    # Solar time (LST) for the given hour
    t_s = UTC_time - 4 * (standard_lon - phi_lon) / 60 + EOT / 60
    omega = rad(15 * (t_s - 12))  # Hour angle in radians
    
    # Solar zenith angle (theta_z)
    theta_z_cos = sin(phi_lat) * sin(delta) + cos(phi_lat) * cos(delta) * cos(omega)
    theta_z_cos = max(-1, min(1, theta_z_cos))  # Clamp to [-1, 1] to avoid domain errors
    theta_z = acos(theta_z_cos)
    
    # Angle of incidence (theta_inc)
    cos_theta_inc = (
        sin(delta) * sin(phi_lat) * cos(theta_tilt) -
        sin(delta) * cos(phi_lat) * sin(theta_tilt) * cos(omega) +
        cos(delta) * cos(phi_lat) * cos(theta_tilt) * cos(omega) +
        cos(delta) * sin(omega) * sin(theta_tilt)
    )
    cos_theta_inc = max(-1, min(1, cos_theta_inc))  # Clamp to [-1, 1]
    theta_inc = acos(cos_theta_inc)
    
    # Hourly direct beam irradiance (DNI approximation)
    DNI = (H_day - H_diff) / cos(theta_z) if cos(theta_z) > 0 else 0
    
    # Direct beam irradiance on the tilted surface
    G_b = DNI * cos(theta_inc) if cos(theta_inc) > 0 else 0
    
    # Diffuse irradiance on the tilted surface
    G_d = H_diff * ((1 + cos(theta_tilt)) / 2)
    
    # Total irradiance on the tilted surface
    G_total = G_b + G_d
    
    # Add ground-reflected irradiance if albedo is provided
    if albedo:
        G_r = H_diff * rho * ((1 - cos(theta_tilt)) / 2)
        G_total += G_r
    
    return G_total