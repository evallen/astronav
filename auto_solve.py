#ASTRONAV
#auto_solve.py

import os
import subprocess
import re
import pandas
import csv
from pathlib import Path


def plate_solve(filename, database = 'v17'):
    '''
    plate_solve: perform plate solving for a single image. results will be written to a .ini and .wcs file of the same name
    NOTE: must have auto_solve.py in same directory as ASTAP installation
    NOTE: databases must be organised in folders according to database name
    :param filename: filename including directory and file extension
    :param database: database name eg. H18, H17, V17, W08 (will default to V17 if none is specified)
    :return: none
    '''

    subprocess.run(["astap", "-f", filename, "-d", database])


def parse_sol(filename):
    """
    parse_sol: parse the .wcs solution file. extract date, time, ra and dec
    :param filename: filename including directory and file extension
    :return: gmt_date: date and time of capture as a pandas datetime object (timestamp)
    :return: ra_val: right ascension value of center of image in decimal degrees (as a float)
    :return: dec_val: declination value of center of image in decimal degrees
    """
    with open(os.path.dirname(filename) + '/' + Path(filename).stem + '.wcs') as file:
        for line in file:
            if line[0:2] == 'JD':
                jd_date = re.findall(r'\d+\.?\d*', line)
                gmt_date = pandas.to_datetime(float(jd_date[0]), origin='julian', unit='D')
            elif line[0:6] == 'CRVAL1':
                ra_val = float(re.findall('-?\d*\.?\d+E[+-]?\d+', line)[0])
            elif line[0:6] == 'CRVAL2':
                dec_val = float(re.findall('-?\d*\.?\d+E[+-]?\d+', line)[0])

    return [gmt_date, ra_val, dec_val]

def write_single_sol(filename, date_ra_dec):
    """
    write_single_sol: write the results of a single solution to a .csv file
    :param filename: filename including directory and file extension
    :param date_ra_dec: array of date, ra, dec
    :return: none
    """
    with open(os.path.dirname(filename) + '/' + Path(filename).stem + '.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([Path(filename).stem, date_ra_dec[0], date_ra_dec[1], date_ra_dec[2]])


def auto_solve(filename):
    """
    auto_solve: plate solve a single image, parse the results and write to its own .csv file
    :param filename: filename including directory and file extension
    :return: none
    """
    plate_solve(filename, 'v17')
    solution = parse_sol(filename)
    write_single_sol(filename, solution)


directory_0 = 'tests/test_0/captures/capture_0/'
filename_0 = 'IMG_3504.CR3'

auto_solve(directory_0 + filename_0)
