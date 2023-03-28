#!/usr/bin/python
import camera
import auto_solve
import multilateration
import sensor
import os
import datetime
import subprocess
import gui

class astronav:
    def __init__(self, astapPath="astap", databasePath="v17"):
        self.camera = camera.camera()
        self.astapPath = astapPath
        self.databasePath = databasePath
        self.sensor = sensor.Sensor()
        #self.multilateration = multilateration.
        self.initiated = False
        self.dir = None
        self.runDir = None
        self.capturesDir = None
        self.skipTake = False
        self.astap = auto_solve.astap(astapPath=astapPath, databasePath=databasePath, debug=False)

    def commandLine(self):
        gui.showGUI()
        #Initiate REPL loop to take in commands and issue instructions to user
        while(True):
            command = input(av.fetchPrompt()).split()

            if(command[0].lower() == "new" or command[0].lower() == "n"):
                if self.initiated:
                    self.sensor.stop()
                self.newCapture()

            if(command[0].lower() == "take" or command[0].lower() == "t"):

                # initiates a new capture if one has not been started yet
                if not self.initiated:
                    self.newCapture()

                # Start capture local capture
                self.sensor.capture()
                imgname, imgpath = self.camera.take(outputdir=self.capturesDir)
                if imgname is None or imgpath is None:
                    print("Camera download failed.")
                    continue
                else:
                    print("Camera download complete.")

                # Process image somehow
                # Push image into plate solving software, try more than one software in early stages
                    # Take in argument to determine which one is used
                    # If none is selected, use default of both and allow user to select which is used
                    # -> Display plate solved image in GUI, OPTIONAL: replace RAW or display side by side
                print("Attempting plate solve...")
                # platesolver = self.astap.auto_solve(filename=imgpath)
                platesolver = self.astap.auto_solve(filename=imgpath)

                # Stop sensor capture
                self.sensor.stopcap()
                
                if(platesolver):
                    print("Ran plate solver")
                else:
                    print("plates not solved. Exiting run and returning to command line")
                    continue
                
                
            if(command[0].lower() == "eval" or command[0].lower() == "e"):
                # Calculate position based on work from other team mates
                self.sensor.stop()
                self.initiated = False

                # needs the Run directory
                self.astap.evaluate_run(f"Runs\\{self.runDir}")
                result = multilateration.calculate_coords(
                    f"Runs\\{self.runDir}\\{self.runDir}.csv",
                    f"Runs\\{self.runDir}\\sensor.txt",
                    datetime.datetime.now().strftime("%D")
                )
                print(result)

                pass

            elif command[0].lower() == "exit" or command[0].lower() == "quit" or command[0].lower() == "q" or command[0].lower() == "e":
                self.sensor.stop()
                self.initiated = False
                return 0
            else:
                print(command)
        pass

    def newCapture(self):
        # Creates the Runs\[run name]\captures older structure
        self.dir = os.getcwd()
        foldername = datetime.datetime.now().strftime("%b-%d-%Y--%I-%M%p")
        self.runDir = dir = foldername
        subprocess.Popen(["mkdir", f"Runs\\{dir}"], shell=True)
        dir = dir + "\\captures"
        subprocess.Popen(["mkdir", f"Runs\\{dir}"], shell=True)
        self.capturesDir = dir

        self.sensor.start(f"Runs\\{self.runDir}\\sensor.txt")
        self.initiated = True

    def takeImage(self):
        # Take image from camera
        # -> display image for user at this point as raw image
        filename, filepath = self.camera.take()
        if filename is None or filepath is None:
            print("Camera download failed. Exiting...")
            return None, None

        print("image taken")
        # Grab sensor data as closely to the image capture as possible
        # Suggestion: Take data before and after and take average? Multithreading?
        # -> Display raw sensor readings on GUI of some sort
        #print("sensors read successfully")
        return filename, filepath

    def displayRawImage(self):
        pass

    def fetchPrompt(self):
        return "astronav> "


# CAUTION: PROGRAM MUST BE RUN ENTIRELY OFFLINE
if __name__ == "__main__":
    print("WELCOME TO ASTRONAV")
    av = astronav(astapPath="C:\\Program Files\\astap\\astap.exe", databasePath="C:\\Program Files\\astap\\v17")
    #Process command line arguments somehow
    av.commandLine()
