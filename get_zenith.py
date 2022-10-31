from astropy.coordinates import Angle, SkyCoord
from astropy import units as u
from skyfield.api import load
from zenith_to_latlon_error import zenith_to_latlon

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
    camera_coord = SkyCoord(ra=ra, dec=dec, frame='icrs')
    zenith_coord = camera_coord.directional_offset_by(
        zenith_direction_ENU,
        (90*u.degree - elevation)
    )
    return zenith_coord.ra, zenith_coord.dec


if __name__ == "__main__":
    ra, dec = get_zenith(
        Angle('5h 55m 11.10s'),
        Angle('+7d 24m 30.6s'),
        #Angle('+31d 48m 45.1s'),
        Angle('+31d 49m 45.1s'),
        Angle('0d'),
        # Angle('+50.47d'),
        Angle('-50.6d'),  # Estimated LAT CORRECT
        # Angle('0d')
    )

    ts = load.timescale()
    time = ts.utc(2022, 10, 24, 5, 25, 51)
    # time = ts.tt_jd(2459876.72629)

    lat, long = zenith_to_latlon(
        ra, dec, time
    )

    print(f"Lat: {lat}, Long: {long}")
