from astropy.coordinates import SkyCoord
from astropy import units as u

# Get the zenith (ra, dec) given:
# 
# Params:
#   ra -- Right ascension of the center of the image (degrees).
#   dec -- Declination of the center of the image (degrees).
#   elevation -- Angle of camera above horizon (degrees).
#   roll -- Angle of camera roll about camera axis (degrees, + for CW)
#   orientation -- Angle of top of image in East-North-Up (ENU) system
#                  (degrees E. of N.)
#
# Returns: (ra, dec)
#   ra -- Right ascension of the zenith (degrees).
#   dec -- Declination of the zenith (degrees).
def get_zenith(ra, dec, elevation, roll, orientation):
    zenith_direction_ENU = orientation + roll
    camera_coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
    zenith_coord = camera_coord.directional_offset_by(
        zenith_direction_ENU*u.degree,
        (90 - elevation)*u.degree
    )
    return zenith_coord.ra, zenith_coord.dec
