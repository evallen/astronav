from astropy.coordinates import Angle
from astropy import units as u
import sys
sys.path.insert(0, '.')

from multilateration import calculate_coords

# Ground truth location - NOT NEEDED FOR CALCULATION
# Just provides information for testing.
# Degrees
true_latitude = 37.23525053101054
true_longitude = -80.41863094

result = calculate_coords(
    platesolve_filepath="tests/baseline_1/baseline_1_ps.csv", 
    sensor_filepath="tests/baseline_1/brennanhouse_test1_2023-02-03.txt",
    sensor_date="2023-02-03",

    # THIS PART IS NOT NECESSARY
    actual_loc=(Angle(true_latitude, unit=u.degree), Angle(true_longitude, unit=u.degree))
)

print(result)
