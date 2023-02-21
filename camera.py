#!/usr/local/bin/python3
import subprocess
import os
        
#python - install --upgrade pip
import serial #python -m pip install pyserial
import time
import datetime


class camera:
	def __init__(self):
		self.ccapi = {
			"URL":	"http://192.168.1.2:8080/ccapi",
			"IP":	"192.168.1.2",			#ccapi network ip number
			"PORT":	"8080",					#ccapi network port number
			"SSID":	"EOSRP as-461_Canon0A",	#canon ccapi wifi name
			"PASS":	"36164039"				#canon ccapi wifi password
		}
		self.debuglevel = ["normal","verbose","debug"]	#list for debug levels in logging
		self.outputpath = os.path.dirname(__file__)	#gets path to python file
	pass

	def take(self, opfile="canomate-api-scripts/takecommand.txt", logging=0, debug=False):
		args = [
			"--ipaddress", f"{self.ccapi['IP']}", 
			"--port", f"{self.ccapi['PORT']}",
			"--opfile", opfile,
			"--outputdir", f"\"{self.outputpath}\\Images\"",
			"--logginglevel", f"{self.debuglevel[logging]}"
        ]
		self.request(args, debug)

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
    def duino(self, file='output.txt'):
		ser = serial.Serial('COM3', 9800, timeout=1)
		time.sleep(2)

		for i in range(50):
			line = ser.readline()
			if line:
				string = line.decode()
				timestamp = str(time.time())
				num = (string)
				#print("val", num)
				#print("time:", timestamp)
				with open(file, 'a') as pyfile:
					pyfile.write(num + ' ' + timestamp + '\n')
		ser.close()


if __name__ == '__main__':
	cam = camera()
	cam.take(debug=True)
	pass

