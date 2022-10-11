import skyfield
from skyfield.api import load, wgs84
from skyfield.positionlib import position_of_radec
import astropy
from astropy.time import Time
from astropy.coordinates import Angle

ts = load.timescale()
t = ts.utc(2022, 10, 11, 20, 5, 15)

earth = 399 # code for earth for something
ra_hours = Angle('16h05m15s').hour
dec_degrees = Angle('37.228963d').degree # example based on astrometry output
pleiades = position_of_radec(ra_hours, dec_degrees, t=t, center=earth)
subpoint = wgs84.subpoint(pleiades)


print('Latitude:', subpoint.latitude)
print('Longitude:', subpoint.longitude)
