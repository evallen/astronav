from skyfield.api import wgs84, load
from skyfield.positionlib import position_of_radec
from astropy.coordinates import Angle

def get_latlon(year, month, day, hour, minute, second, ra_angle, dec_angle):
    ts = load.timescale()
    t = ts.utc(year, month, day, hour, minute, second)

    earth = 399 # code for earth for something
    ra_hours = ra_angle.hour
    dec_degrees = dec_angle.degree # example based on astrometry output
    pleiades = position_of_radec(ra_hours, dec_degrees, t=t, center=earth)
    subpoint = wgs84.geographic_position_of(pleiades)

    return subpoint.latitude, subpoint.longitude

if __name__ == "__main__":
    print(get_latlon(2022, 10, 11, 20, 5, 15, Angle('16h05m15s'), Angle('37.228963d')))