from skyfield.api import wgs84, load
from skyfield.positionlib import position_of_radec

def zenith_to_latlon(zra, zdec, time):
    earth = 399 # code for earth for something
    ra_hours = zra.hour
    dec_degrees = zdec.degree # example based on astrometry output
    epoch = load.timescale().utc(2000, 1, 1, 0, 0, 0)
    pleiades = position_of_radec(ra_hours, dec_degrees, t=time, center=earth)
    subpoint = wgs84.geographic_position_of(pleiades)

    return subpoint.latitude, subpoint.longitude
    

