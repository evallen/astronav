#!/usr/local/bin/python3
import subprocess
import os
        
#python - install --upgrade pip
import serial #python -m pip install pyserial
import time
import datetime
import threading
import datetime

class camera:
	def __init__(self):
		self.ccapi = {T
			"URL":	"http://192.168.1.2:8080/ccapi",
			"IP":	"192.168.1.2",			#ccapi network ip number
			"PORT":	"8080",					#ccapi network port number
			"SSID":	"EOSRP as-461_Canon0A",	#canon ccapi wifi name
			"PASS":	"36164039"				#canon ccapi wifi password
		}
		self.debuglevel = ["normal","verbose","debug"]	#list for debug levels in logging
		self.outputpath = os.path.dirname(__file__)	#gets path to python file
		self.mutex = Lock()
	pass

	def take(self, opfile="canomate-api-scripts/takecommand.txt", logging=0, debug=False):
		args = [
			"--ipaddress", f"{self.ccapi['IP']}", 
			"--port", f"{self.ccapi['PORT']}",
			"--opfile", opfile,
			"--outputdir", f"\"{self.outputpath}\\Images\"",
			"--logginglevel", f"{self.debuglevel[logging]}"
        ]
		#defines threads for camera take and for sensor gathering
		camerathread = threading.Thread(target=self.request, args=(args, debug))
		sensorthread = threading.Thread(target=self.duino, args=())

		#This creates a folder with the datetime for separating files
		foldername = datetime.datetime.now().strftime("%I-%M%p-%B-%d-%Y")
		subprocess.Popen([f"mkdir {foldername}"], shell=True)
  
		# Starts threads
		sensorthread.start()
		sleep(2)				#Sleep for 2 to allow sensor to start before camera image takes
		camerathread.start()
  
		# Joins threads
		sensorthread.join()
		camerathread.join()
		

	def help(self, debug=False):
		args = ["--help"]
		self.request(args, debug)
  
	def info(self, debug=False):
		args = ["--op", "PrintCameraInfo | PrintCameraDateTime | PrintShootingSettings | PrintShootingModeDial | PrintLensInfo | PrintBatteryInfo | PrintTemperatureStatus"]
		self.request(args, debug)
  
	def request(self, args, debug=False):
		process = [
      		"python3", "Canomate/Canomate.py"
		]
  
		process = process + args
		if debug: print(process)
		sp = subprocess.Popen(process, shell=True, stdout=subprocess.PIPE)
		while sp.poll() is None:
			line = sp.stdout.readline().decode()
			print(line, end='')
       
       
    #modify this to run constantly polling and storing arduino data, but use 
    def duino(self, file='output.txt', iter=50, debug=False):
		ser = serial.Serial('COM3', 9800, timeout=1)
		time.sleep(2)
		pyfile = open(file, 'a')

		for i in range(iter):
			line = ser.readline()
			if line:
				string = line.decode()
				timestamp = str(time.time())
				num = (string)
				if debug:
					print("val", num, end='')
					print("\ttime:", timestamp)
				pyfile.write(num + ' ' + timestamp + '\n')
		ser.close()


if __name__ == '__main__':
	cam = camera()
	cam.take(debug=True)
	pass

