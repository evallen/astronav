#!/usr/bin/python
import camera
import auto_solve

import sys, getopt

class astronav:
    def __init__(self, astapPath="astap", databasePath="v17"):
        self.camera = camera.camera()
        self.astapPath = astapPath
        self.databasePath = databasePath
        self.astap = auto_solve.astap(astapPath=astapPath, databasePath=databasePath, debug=False)
        


    def commandLine(self):
        #Initiate REPL loop to take in commands and issue instructions to user
        while(True):
            command = input(av.fetchPrompt()).split()

            if(command[0].lower() == "take" or command[0].lower() == "t"):
                imgname, imgpath = av.takeImage()
                if imgname is None or imgpath is None:
                    print("Camera download failed. Exiting...")
                    return None, None

                #Process image somehow
                #Push image into plate solving software, try more than one software in early stages
                    #Take in argument to determine which one is used
                    #If none is selected, use default of both and allow user to select which is used
                    # -> Display plate solved image in GUI, OPTIONAL: replace RAW or display side by side
                #imgpath = "G:\\My Drive\\vt\\Engineering\\4805-4806 Senior Design\\astronav\\Runs\\Mar-02-2023--10-01PM\\IMG_3544.CR3"
                #imgpath2 = "G:/'My Drive'/vt/Engineering/'4805-4806 Senior Design'/astronav/Runs/Mar-02-2023--10-01PM/IMG_3544.CR3"
                #imgname = "IMG_3544.CR3"
                platesolver = self.astap.auto_solve(filename=imgpath)
                if(platesolver):
                    print("plates solved")
                else:
                    print("plates not solved. Exiting run and returning to command line")
                    continue
                #Calculate position based on work from other team mates

                X = "NOT IMPLEMENTED"
                Y = "NOT IMPLEMENTED"
                Z = "NOT IMPLEMENTED"

                # Push coordinates into error calculation unit and output to user with data
                # -> Display raw coordinates on GUI display or command line

                XERROR = "NOT IMPLEMENTED"
                YERROR = "NOT IMPLEMENTED"
                ZERROR = "NOT IMPLEMENTED"
                print("Position X: " + X + "\t\tError: " + XERROR)
                print("Position Y: " + Y + "\t\tError: " + YERROR)
                print("Position Z: " + Z + "\t\tError: " + ZERROR)

                #OPTIONAL: display coordinates on some sort of offline map data software/program
                # -> Display map in final result
            elif command[0].lower() == "exit" or command[0].lower() == "quit":
                return 0


            else:
                print(command)
        pass

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
