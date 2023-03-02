#ASTRONAV
#auto_solve.py

import os
import subprocess
import re
import pandas
import csv
from pathlib import Path
import pandas as pd
import glob


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
    if os.path.isfile(os.path.dirname(filename) + '/' + Path(filename).stem + '.wcs'):
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
    else:
        return ['F', 'F', 'F']


def write_single_sol(filename, date_ra_dec):
    """
    write_single_sol: write the results of a single solution to a .csv file
    :param filename: filename including directory and file extension
    :param date_ra_dec: array of date, ra, dec
    :return: none
    """
    if os.path.isfile(os.path.dirname(filename) + '/' + Path(filename).stem + '.wcs'):
        with open(os.path.dirname(filename) + '/' + os.path.basename(os.path.dirname(filename)) + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Image', 'Dec', 'RA ', 'Date', 'Time'])
            writer.writerow([Path(filename).stem,  date_ra_dec[1], date_ra_dec[2], date_ra_dec[0].date(), date_ra_dec[0].time()])
    else:
        with open(os.path.dirname(filename) + '/' + os.path.basename(os.path.dirname(filename)) + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Image', 'Dec', 'RA ', 'Date', 'Time'])
            writer.writerow([Path(filename).stem, 'f', 'f', 'f', 'f'])



def evaluate_run(test_directory):
    """
    evaluate_run: after solving all the caputres in a test, write a CSV file with all the results
    :param test_directory: test directory is the "tests/???" directory containing something like
        test_0/
            captures/
                capture_0/
                capture_1/
                ...
            ...
    eg. evaluate_run(c:/test0) should have test0/captures/captures0
    :return: none
    """

    captures_dir = f"{test_directory}/captures/"
    test_name = os.path.basename(test_directory)
    all_dirs = next(os.walk(captures_dir))[1]
    print(test_name)

    all_files = []
    for dirs in all_dirs:
        all_files.append(captures_dir + '/' + dirs + '/' + dirs + '.csv')
    print(all_dirs)

    li = pd.DataFrame()

    for filename in all_files:
        df = pd.read_csv(filename)
        li = pd.concat([li, df], ignore_index=True)
    # print(os.path.basename(str(Path(test_directory).parents[0])))
    li.to_csv(test_directory + "/" + test_name + '.csv', index=False)


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

directory_1 = 'tests/test_0/captures/capture_1/'
filename_1 = 'IMG_3505.CR3'

directory_2 = 'tests/test_0/captures/capture_2/'
filename_2 = 'IMG_3506.CR3'

directory_3 = 'tests/test_0/captures/capture_3/'
filename_3 = 'IMG_3509.CR3'

directory_4 = 'tests/test_0/captures/capture_4/'
filename_4 = 'IMG_3510.CR3'

directory_5 = 'tests/test_0/captures/capture_5/'
filename_5 = 'IMG_3511.CR3'

#auto_solve(directory_0 + filename_0)
#auto_solve(directory_1 + filename_1)
#auto_solve(directory_2 + filename_2)
#auto_solve(directory_3 + filename_3)
#auto_solve(directory_4 + filename_4)
#auto_solve(directory_5 + filename_5)

#evaluate_run('tests/test_0')
