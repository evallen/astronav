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

# python3 - install --upgrade pip --user
# python3 -m pip install -U pandas

class astap:
    def __init__(self, astapPath="C:\\Program Files\\astap.exe", databasePath="C:\\Program Files\\astap\\v17", debug=False):
        self.exePATH = rf"{astapPath}"
        self.dbPATH = rf"{databasePath}"
        self.debug = debug


    def plate_solve(self, filename, database = 'v17'):
        '''
        plate_solve: perform plate solving for a single image. results will be written to a .ini and .wcs file of the same name
        NOTE: must have auto_solve.py in same directory as ASTAP installation
        NOTE: databases must be organised in folders according to database name
        :param filename: filename including directory and file extension
        :param database: database name eg. H18, H17, V17, W08 (will default to V17 if none is specified)
        :return: none
        '''
        print(filename)
        command = [self.exePATH, "-f", rf"{filename}", "-d", self.dbPATH, "-r 180"]
        if self.debug: 
            print("EXE:\t" + self.exePATH)
            print("FILE:\t" + filename)
            print("PATH:\t" + self.dbPATH)
            print("COMMAND:\t" + str(command))

        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        while sp.poll() is None:
            line = sp.stdout.readline().decode()


    def parse_sol(self, filename):
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


    def write_single_sol(self, filename, date_ra_dec):
        """
        write_single_sol: write the results of a single solution to a .csv file
        :param filename: filename including directory and file extension
        :param date_ra_dec: array of date, ra, dec
        :return: none
        """
        filename = os.path.join("\\".join(filename.split("\\")[:-1]), "".join(filename.split("\\")[-1].split(".")[0]) + ".csv") # HAHA did you KNOW DIRECTORIES can have EXTENSIONS? I DIDNT LMAO
        
        touch = ["type", "nul", ">", rf"{filename}" ]   #touch command for windows. TODO: add a way to determine OS
        subprocess.run(touch, shell=True, stdout=subprocess.PIPE)
        with open(fr"{filename}", 'w+t', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['dec', 'ra', 'date', 'time'])
            if "F" in date_ra_dec:
                writer.writerow([Path(filename).stem, 'f', 'f', 'f', 'f'])
            else:
                print(f"RA: {date_ra_dec[1]}")
                print(f"Dec: {date_ra_dec[2]}")
                writer.writerow([date_ra_dec[2], date_ra_dec[1], date_ra_dec[0].strftime('%m/%d/%Y'), date_ra_dec[0].strftime('%I:%M:%S')])
            

    def evaluate_run(self, test_directory):
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

        test_name = os.path.basename(test_directory)
        captures_dir = r'{test_directory}\captures\*\*.CR3*'


        all_files = []
        for file in glob.glob(captures_dir, recursive=True):
            all_files.append(file)

        li = pd.DataFrame()

        for filename in all_files:
            df = pd.read_csv(filename)
            if df['ra'][0] != 'f':
                li = pd.concat([li, df], ignore_index=True)
        li.to_csv(test_directory + "/" + test_name + '.csv', index=False)

    def auto_solve(self, filename):
        """
        auto_solve: plate solve a single image, parse the results and write to its own .csv file
        :param filename: filename including directory and file extension
        :return: none
        """
        self.plate_solve(filename, 'v17')
        solution = self.parse_sol(filename)
        if solution == 1:
            return False
        self.write_single_sol(filename, solution)

        return True

if __name__ == '__main__':
    pass
