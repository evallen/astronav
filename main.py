#!/usr/bin/python

import sys, getopt


# CAUTION: PROGRAM MUST BE RUN ENTIRELY OFFLINE
def main():
    pass
    #Process command line arguments somehow

    #Initiate REPL loop to take in commands and issue instructions to user

    #Take image from camera
        # -> display image for user at this point as raw image

    #Grab sensor data as closely to the image capture as possible
        #Suggestion: Take data before and after and take average? Multithreading?
        # -> Display raw sensor readings on GUI of some sort

    #Process image somehow
    #Push image into plate solving software, try more than one software in early stages
        #Take in argument to determine which one is used
        #If none is selected, use default of both and allow user to select which is used
        # -> Display plate solved image in GUI, OPTIONAL: replace RAW or display side by side

    #Calculate position based on work from other team mates

    #Push coordinates into error calculation unit and output to user with data
    # -> Display raw coordinates on GUI display or command line

    #OPTIONAL: display coordinates on some sort of offline map data software/program
    # -> Display map in final result

if __name__ == "__main__":
   main()