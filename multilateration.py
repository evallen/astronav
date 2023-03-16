from scipy.optimize import least_squares
import time
import numpy as np
from astropy import units as u
from astropy.coordinates import Angle, angular_separation
from zenith_to_latlon_error import get_latlon
from skyfield.api import load
from typing import Tuple, List
from dataclasses import dataclass
import re
import pandas as pd


# This code is heavily based off of the example at
# https://github.com/koru1130/multilateration/blob/master/multilateration.py

# --- Begin adapted section --------------------------------------------------------------

def _residuals_fn(points, dist):
    """
    Defines a residuals function for least squares optimization.
    In our case, the "residuals" for a given (latitude, longitude, bias)
    are the distance that the (latitude, longitude) is from each multilateration
    circle (adjusted for bias). 

    So if we try a (latitude, longitude) point that is 1 arcsecond away from
    one of the multilateration circles, the residual for that would be 1 arcsecond.

    Params:
    -- points: List of Earth points in the format
        ((lat, lon), zd) where
        -- lat: Latitude (astropy Angle)
        -- lon: Longitude (astropy Angle)
        -- zd: Zenith distance (astropy Angle)
    
    -- dist: Distance function to compute the distance between points.

    Returns: 
        A function that computes a list of residuals for a given 
        (latitude, longitude, bias) point. 
    """
    def fn(args):
        lat, lon, bias = args
        location = (lat, lon)
        return np.array([(dist(p, location) - r - bias) for (p, r) in points])
    return fn


def _multilateration(points):
    """
    Do multilateration. Internal helper method.
    Uses least squares optimization.

    Params:
    -- points: List of Earth points in the format
        ((lat, lon), zd) where
        -- lat: Latitude (astropy Angle)
        -- lon: Longitude (astropy Angle)
        -- zd: Zenith distance (astropy Angle)
    
    Returns:
        Found optimal latitude / longitude that we are probably at.
    """
    dist = _angular_dist

    ps = [x[0] for x in points]
    x0 = np.mean(np.array(ps), axis=0)
    x0 = np.append(x0, 0)  # Add 0 bias

    bias_bounds = Angle('50d').radian

    return least_squares(
        _residuals_fn(points, dist), 
        x0, 
        bounds=(
            [-np.inf, -np.inf, -bias_bounds],
            [+np.inf, +np.inf, +bias_bounds],
        ),
    )

# --- End adapted section ----------------------------------------------------------------

# --- Helper methods ---------------------------------------------------------------------

def _angular_dist(latlon1, latlon2):
    """
    Find the angular distance between two latitude / longitude points.
    All quantities should be astropy Angles or floats. If they are floats,
    they are interpreted as radians.

    Params:
    -- latlon1: The first tuple of (latitude, longitude).
    -- latlon2: The second tuple of (latitude, longitude).

    Returns:
        The angular distance between `latlon1` and `latlon2`.
    """
    (lat1, lon1) = latlon1
    (lat2, lon2) = latlon2
    sep = angular_separation(lon1, lat1, lon2, lat2)
    return sep


def _parse_line_OLD(line: str, date: str, sensor_timezone: int) -> pd.Series:
    """
    Parse a line of the sensor data.

    Params:
    -- line: The string line from the file to parse.
    -- date: The date of the measurement in the format "MM/DD/YYYY" without leading
        zeroes.
    -- sensor_timezone: Timezone of the sensor as an integer GMT offset (so GMT-5 is -5).

    Returns: 
        Dataframe row containing the sensor measurements and time for that line.
    """
    result = re.match(r"([0-9.:]+)\s*X Tilt: ([0-9]+\.[0-9]+).*Y Tilt: ([0-9]+\.[0-9]+).*Z Tilt: ([0-9]+\.[0-9]+)\s*", line)
    row = pd.Series({
        "time": pd.Timestamp(f"{date} {result.group(1)}") - pd.Timedelta(hours=sensor_timezone),
        "x": float(result.group(2)),
        "y": float(result.group(3)),
        "z": float(result.group(4))
    })
    return row


def _read_sensor_txt(path: str, date: str) -> pd.DataFrame:
    """
    Get the Pandas dataframe corresponding to the sensor data from the sensor
    output file specified.

    Params:
    -- path: Path to the sensor file.
    -- date: Date of the sensor reading in the format "MM/DD/YYYY" without leading zeroes.

    Returns:
        Dataframe with the sensor data.
    """
    df = pd.read_csv(path, names=["time", "x", "y", "z"],
                     dtype={
                        "time": np.float64,
                        "x": np.float64,
                        "y": np.float64,
                        "z": np.float64,
                     })
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    return df


def _read_sensor_txt_OLD(path: str, date: str) -> pd.DataFrame:
    """
    Get the Pandas dataframe corresponding to the sensor data from the sensor
    output file specified.

    Params:
    -- path: Path to the sensor file.
    -- date: Date of the sensor reading in the format "MM/DD/YYYY" without leading zeroes.

    Returns:
        Dataframe with the sensor data.
    """
    with open(path) as file:
        df = pd.DataFrame(_parse_line_OLD(line, date) for line in file.readlines())
    
    return df


def _get_averaged_reading(reading_data: pd.DataFrame, col: str, exposure_start: pd.Timestamp, exposure_duration: pd.Timedelta) -> float:
    """
    Get the averaged (median) reading from a set of data.

    Params:
    -- reading_data: Sensor data after parsing from file.
    -- col: The name of the column to average.
    -- exposure_start: Timestamp when the exposure begins.
    -- exposure_duration: How long the exposure lasts.

    Returns:
        The median reading of the column selected during the period specified.
    """
    our_data = reading_data[reading_data['time'].between(exposure_start, exposure_start + exposure_duration)]
    median = our_data[col].median()
    return median


def _get_angle(reading_data: pd.DataFrame, exposure_start: pd.Timestamp, exposure_duration: pd.Timedelta) -> Angle:
    """
    Get the angle of a measurement from sensor data.

    Params:
    -- reading_data: Sensor data after parsing from the file.
    -- exposure_start: Timestamp when the exposure begins.
    -- exposure_duration: How long the exposure lasts.

    Returns:
        Angle representing the altitude of the measurement.
    """
    average = _get_averaged_reading(reading_data, 'y', exposure_start, exposure_duration)
    return Angle(average, unit=u.deg)


def _get_date_tuple(datestr, timestr):
    """
    Get a tuple of ints from a date string and time string.

    Params:
    -- datestr: Date string in the form "MM/DD/YYYY" without leading
        zeroes.
    -- timestr: Time string in the form "HH:MM:SSSS" without leading 
        zeroes.
    
    Returns:
        Tuple of ints (year, month, day, hour, min, sec)
    """
    month, day, year = [int(x) for x in datestr.split('/')]
    hour, min, sec = [int(x) for x in timestr.split(':')]
    return (year, month, day, hour, min, sec)


# --- dataclasses ------------------------------------------------------------------------

@dataclass
class StarInfo:
    """
    Stores information about a plate-solved star.
    """
    ra: Angle
    dec: Angle 
    alt: Angle
    time: Tuple[int]

    def zd(self): 
        """Zenith distance calculation."""
        return Angle('90d') - self.alt

    def latlon(self):
        """Find the ground point of the given star in latitude
        and longitude."""
        return get_latlon(*self.time, self.ra, self.dec)


@dataclass
class MultilaterationResult:
    """
    Stores information about a multilateration calculation,
    including calculated location and error from actual
    location if known.
    """
    elapsed_time: float
    lat: Angle
    lon: Angle
    alt_bias: Angle
    err_angular: Angle | None
    err_nm: float | None

    def __str__(self):
        out = ""
        out += f"Elapsed: {self.elapsed_time}s\n"
        out += f"Latitude: {self.lat.to_string(unit=u.degree)}\n"
        out += f"Longitude: {self.lon.to_string(unit=u.degree)}\n"
        out += f"Alt. Bias: {self.alt_bias.to_string(unit=u.degree)}\n"
        
        if self.err_angular is not None:
            out += f"Err. Angular Separation: {self.err_angular.to_string(unit=u.degree)} \n"
            out += f"Err. in NM: {self.err_nm}\n"
        else:
            out += f"Err. Angular Separation: ??? [actual unknown] \n"
            out += f"Err. in NM: ??? [actual unknown] \n"
        return out


# --- Publicly accessible methods ----------------------------------------------------

def calculate_coords(platesolve_filepath: str, sensor_filepath: str,
                     sensor_date: str,
                     duration: pd.Timedelta = pd.Timedelta(seconds=8),
                     actual_loc: Tuple[Angle|None] = (None, None)):
    """
    Calculate coordinates of the user.

    Params:
     -- platesolve_filepath: The path to the plate solve CSV file.
            The columns should be:
                "ra": Right ascension of each star, in degrees (float)
                "dec": Declination of each star, in degrees (float)
                "date": Date of each star measurement, in format MM/DD/YYYY (no leading
                        zeroes)
                        (like 2/4/2023)
                "time": Time of each measurement (GMT+0), in format HH:MM:SS (no leading
                        zeroes)
                        (like 1:41:43)
     -- sensor_filepath: The path to the sensor data capture file.
     -- sensor_date: String of the date the sensor data was captured, like
            "2023-02-03" for February 03rd, 2023.
     -- duration: How long each capture is.
     -- actual_loc: Tuple of the actual latitude / longitude in Astropy Angles (or (None, None)) if
            unknown. Used for evaluating the result.

    Returns:
        MultilaterationResult containing the calculated coordinates of the user.
    """
    actual_lat, actual_lon = actual_loc
    ps_data = pd.read_csv(platesolve_filepath)
    data = _read_sensor_txt(sensor_filepath, sensor_date)

    stardata = [StarInfo(
        ra=Angle(ra, unit=u.degree),
        dec=Angle(dec, unit=u.degree),
        alt=_get_angle(
            data,
            pd.Timestamp(f"{date} {time}"),
            duration,
        ),
        time=_get_date_tuple(date,time)
    ) for ra,dec,date,time in zip(ps_data['ra'], ps_data['dec'], ps_data['date'], ps_data['time'])]

    result = run_multilateration(
        stardata,
        actual_lat,
        actual_lon
    )

    return result


def run_multilateration(stardata: List[StarInfo], actual_latitude: Angle = None, actual_longitude: Angle = None) -> MultilaterationResult:
    """
    Run multilateration on some star data.

    Params:
    -- stardata: List of StarInfo structs, each representing one star.
    -- actual_latitude: Actual latitude of the user if known for testing.
    -- actual_longitude: Actual longitude of the user if known for testing.

    Returns:
        MultilaterationResult with the found coordinates and error if the 
        actual coordinates are known.
    """
    # radian vs radians below is because lat / lon coordinates are Skyfield Angles
    # whereas the zd coordiantes are astropy angles
    points = [([l.radians for l in p.latlon()], p.zd().radian) for p in stardata]

    before = time.time()
    result_lat_rads, result_lon_rads, result_alt_bias_rads = _multilateration(points).x
    elapsed = time.time() - before

    result_lat = Angle(result_lat_rads, u.radian)
    result_lon = Angle(result_lon_rads, u.radian)
    result_alt_bias = Angle(result_alt_bias_rads, u.radian)

    if actual_latitude is not None and actual_longitude is not None:
        error_angular = _angular_dist((result_lat.radian, result_lon.radian), (actual_latitude.radian, actual_longitude.radian))
        error_angular = Angle(error_angular, u.radian)
        error_nm = error_angular.arcminute
    else:
        error_angular = None
        error_nm = None

    return MultilaterationResult(elapsed, result_lat, result_lon, result_alt_bias, error_angular, error_nm)

