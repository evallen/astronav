from scipy.optimize import least_squares
import time
import numpy as np
from astropy import units as u
from astropy.coordinates import Angle, angular_separation
from zenith_to_latlon_error import get_latlon
from skyfield.api import load

# This code is heavily based off of the example at
# https://github.com/koru1130/multilateration/blob/master/multilateration.py

# --- Begin adapted section --------------------------------------------------------------

def residuals_fn(points, dist):
    def fn(args):
        #return np.array([(dist(p, location).km - r)*(r*r) for (p, r) in points])
        lat, lon, bias = args
        location = (lat, lon)
        return np.array([(dist(p, location) - r - bias) for (p, r) in points])
    return fn

def multilateration(points):
    dist = angular_dist

    ps = [x[0] for x in points]
    x0 = np.mean(np.array(ps), axis=0)
    x0 = np.append(x0, 0)  # Add 0 bias

    bias_bounds = Angle('5d').radian

    return least_squares(
        residuals_fn(points, dist), 
        x0, 
        bounds=(
            [-np.inf, -np.inf, -bias_bounds],
            [+np.inf, +np.inf, +bias_bounds],
        ),
    )

# --- End adapted section ----------------------------------------------------------------

# Helper method
def angular_dist(latlon1, latlon2):
    (lat1, lon1) = latlon1
    (lat2, lon2) = latlon2
    sep = angular_separation(lon1, lat1, lon2, lat2)
    return sep

if __name__ == "__main__":
    # Params
    alt_bias = Angle('3d')

    # Actual
    actual_latitude = Angle('+37d 10m 44.76s')
    actual_longitude = Angle('-80d 21m 5.41s')

    measure_time = (2022, 10, 24, 5, 25, 51)

    # Betelgeuse
    betelgeuse_ra = Angle('5h 55m 11.10s')
    betelgeuse_dec = Angle('+7d 24m 30.6s')
    betelgeuse_alt = Angle('+31d 48m 45.1s') + alt_bias
    betelgeuse_zd = Angle('90d') - betelgeuse_alt
    betelgeuse_lat, betelgeuse_lon = get_latlon(*measure_time, betelgeuse_ra, betelgeuse_dec)

    # Algenib
    algenib_ra = Angle('0h 13m 15.31s')
    algenib_dec = Angle('+15d 11m 10.1s')
    algenib_alt = Angle('+55d 32m 08.6s') + alt_bias
    algenib_zd = Angle('90d') - algenib_alt
    algenib_lat, algenib_lon = get_latlon(*measure_time, algenib_ra, algenib_dec)

    # Schedar
    schedar_ra = Angle('0h 40m 32.73s')
    schedar_dec = Angle('+56d 32m 24.7s')
    schedar_alt = Angle('+65d 07m 21.8s') + alt_bias
    schedar_zd = Angle('90d') - schedar_alt
    schedar_lat, schedar_lon = get_latlon(*measure_time, schedar_ra, schedar_dec)

    # radian vs radians below is because lat / lon coordinates are Skyfield Angles
    # whereas the zd coordiantes are astropy angles
    points = [
        ((betelgeuse_lat.radians, betelgeuse_lon.radians), betelgeuse_zd.radian),
        ((algenib_lat.radians, algenib_lon.radians), algenib_zd.radian),
        ((schedar_lat.radians, schedar_lon.radians), schedar_zd.radian),
    ]

    before = time.time()
    result_lat_rads, result_lon_rads, result_alt_bias_rads = multilateration(points).x
    print(f"Took {time.time() - before} sec")
    
    result_lat = Angle(result_lat_rads, u.radian)
    result_lon = Angle(result_lon_rads, u.radian)
    result_alt_bias = Angle(result_alt_bias_rads, u.radian)

    print(f"Latitude: {result_lat.to_string(unit=u.degree)}")
    print(f"Longitude: {result_lon.to_string(unit=u.degree)}")
    print(f"Bias: {result_alt_bias.to_string(unit=u.degree)}")

    error_angular = angular_dist((result_lat.radian, result_lon.radian), (actual_latitude.radian, actual_longitude.radian))
    error_angular = Angle(error_angular, u.radian)
    print(f"Error Angular Separation: {error_angular.to_string(unit=u.degree)} ")

    error_nm = error_angular.arcminute
    print(f"Error in NM: {error_nm}")