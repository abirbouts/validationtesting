"""
This module contains functions to calculate the total solar irradiance on a tilted surface using Global Horizontal Irradiance (GHI)
 and Diffuse Horizontal Irradiance (DHI) or Direct Normal Irradiance (DNI) and Diffuse Horizontal Irradiance (DHI).
"""

from math import radians as rad, sin, cos, acos, degrees, pi
import logging
import numpy as np
import datetime as dt
from datetime import datetime
import pytz

def with_GHI_DHI(
    theta_tilt: float, 
    GHI: float, 
    DHI: float, 
    rho: float, 
    lat: float, 
    lon: float,
    day_of_year: int, 
    time: datetime, 
    time_zone: float,
    azimuth: float) -> float:
    """
    Calculate the total solar irradiance on a tilted surface using Global Horizontal Irradiance (GHI) 
    and Diffuse Horizontal Irradiance (DHI).
    """
    time_zone_obj = pytz.timezone(time_zone)
    time = time_zone_obj.localize(time)
    offset = time.utcoffset() / dt.timedelta(hours=1)
    rad_theta_tilt = rad(theta_tilt)
    rad_lat = rad(lat)
    rad_lon = rad(lon)
    rad_azimuth = rad(azimuth)
    
    B = 360 * ((day_of_year-1)/365) # day angle
    rad_B = rad(B)  
    
    delta = 23.45 * sin(rad(360*((284+day_of_year)/365)))  # solar declination angle
    rad_delta = rad(delta)
    
    EOT = 229.2 * (0.000075 + 0.001868 * cos(rad_B) - 0.032077 * sin(rad_B) - 0.014615 * cos(2 * rad_B) - 0.04089 * sin(2 * rad_B))  # equation of time
    
    LST = (time.hour + (lon / 15 - offset) + (EOT / 60)) % 24
    
    omega = 15 * (LST - 12)  # hour angle
    rad_omega = rad(omega)
    
    # Solar zenith angle (theta_z)
    cos_theta_z = sin(rad_lat) * sin(rad_delta) + cos(rad_lat) * cos(rad_delta) * cos(rad_omega)
    rad_theta_z = acos(cos_theta_z)

    # Direct Normal Irradiance (DNI)
    if cos_theta_z > 0.1:
        DNI = (GHI - DHI) / cos(rad_theta_z)
    else:
        DNI = 0
        
    rad_azimuth_sun = np.sign(omega) * abs((acos((cos(rad_theta_z) * sin(rad_lat) - sin(rad_delta)) / (sin(rad_theta_z) * cos(rad_lat)))))  # solar azimuth angle

    # Angle of incidence (theta_inc)
    cos_theta_inc = (
        sin(rad_delta) * sin(rad_lat) * cos(rad_theta_tilt) -
        sin(rad_delta) * cos(rad_lat) * sin(rad_theta_tilt) * cos(rad_azimuth) +
        cos(rad_delta) * cos(rad_lat) * cos(rad_theta_tilt) * cos(rad_omega) +
        cos(rad_delta) * sin(rad_lat) * sin(rad_theta_tilt) * cos(rad_azimuth) * cos(rad_omega) +
        cos(rad_delta) * sin(rad_omega) * sin(rad_theta_tilt) * sin(rad_azimuth)
    )

    cos_theta_inc = max(-1, min(1, cos_theta_inc))  # Clamp to [-1, 1]
    rad_theta_inc = acos(cos_theta_inc)
        
    # Direct beam irradiance (I_beam)
    I_beam = DNI * cos(rad_theta_inc)
    
    # Diffuse irradiance (I_diffuse)
    I_diffuse = DHI * ((1 + cos(rad_theta_tilt)) / 2)
    
    # Ground-reflected irradiance (I_reflected)
    I_reflected = GHI * rho * ((1 - cos(rad_theta_tilt)) / 2)

    # Total irradiance
    I_total = I_beam + I_diffuse + I_reflected
    return I_total


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
