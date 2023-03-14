#!/usr/local/bin/python3
import subprocess
import os
        
#python - install --upgrade pip
#import serial #python -m pip install -U pyserial
import time
import datetime
import threading
import datetime
import sys

# simple capture object for csv grabbing
class Capture:
	def __init__(self, time, x_tilt, y_tilt, z_tilt):
		self.time = time; self.x_tilt = x_tilt
		self.y_tilt = y_tilt; self.z_tilt = z_tilt
	def __str__(self):
		return (str(self.time) + ", " + str(self.x_tilt) + ", " + 
				str(self.y_tilt) + ", " + str(self.z_tilt))
				
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
		self.mutex = threading.Lock()

		# arduino globals
		self.start_capture = False
		self.end_capture = False
		self.recording = True
		self.debug = 0

		# start arduino thread
		self.sensorthread = threading.Thread(target=self.duino, args=())
		self.sensorthread.start()
		pass


	# outputdir would not have \ at the beginning
	# TODO add in catches for \
	def take(self, opfile="camera/takecommand.txt", logging=0, debug=False, outputdir = ""):
		# TODO: Flush the images taken before the run using a for loop
		"""
		done = False
		while (!done) {
			# Sample Output
			# ** Download Failed ** "[Errno 2] No such file or directory: 'G:\\My Drive\\School(VT)\\Engineering\\4805-4806 Senior Design\\astronav\\Runs\\12-48PM-February-28-2023\\IMG_3539.CR3'"
			lines = self.take(opfile="download.txt", debug=debug)
			if "some line that means nothing to grab" in lines:
				done = True
		}
		"""

		#This creates a folder with the datetime for separating
		foldername = datetime.datetime.now().strftime("%b-%d-%Y--%I-%M%p")
		subprocess.Popen(["mkdir", f"Runs\\{outputdir}{foldername}"], shell=True)
		
		dumpfolder = f"{self.outputpath}\\Runs\\{outputdir}{foldername}"
		args = [
			"--ipaddress", f"{self.ccapi['IP']}", 
			"--port", f"{self.ccapi['PORT']}",
			"--opfile", opfile,
			"--outputdir", f"{dumpfolder}",
			"--logginglevel", f"{self.debuglevel[logging]}"
        ]

		return self.request(args=args, debug=debug)

		#defines threads for camera take and for sensor gathering
		#camerathread = threading.Thread(target=self.request, args=(args, debug))
		#sensorthread = threading.Thread(target=self.duino, args=())

		# Starts threads
		#sensorthread.start()
		#time.sleep(2)				#Sleep for 2 to allow sensor to start before camera image takes
		#camerathread.start()
  
		# Joins threads
		#sensorthread.join()
		#camerathread.join()

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

			if (debug): print(line, end='')
			if "DownloadNewFilesPolled" in line:
				#Sample output ['GET', '/ccapi/ver100/contents/sd/117_PANA/IMG_3535.CR3', 'Downloading', '/ccapi/ver100/contents/sd/117_PANA/IMG_3535.CR3...', 'DownloadNewFilesPolled:', 'IMG_3535.CR3', 'stored', 'at', 'G:\\My', 'Drive\\School(VT)\\Engineering\\4805-4806', 'Senior', 'Design\\astronav\\Images\\IMG_3535.CR3', '[download', 'time', '=', '11.34', '(s)]']
				splitline = line.split()
				if debug:
					print("~~~")
					print(splitline)
					print("~~~")
				if len(splitline) > 6:
					imgname = splitline[5]
					imgpath = " ".join(splitline[8:-5])
					print(f"Filename: {imgname}\t{imgpath}")
					return imgname, imgpath
				if "No" in splitline:
					print(" ".join(splitline[1:4] + " Capture"))
		return None, None	#Check this return type in 
       
	def duino(self, file='output.txt'):
		# port is a device name: depending on operating system. e.g. /dev/ttyUSB0 on GNU/Linux or COM3 on Windows.
		# Add compatibility for linux and windows
		import serial
		ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
		ser.setDTR(False) # Drop DTR
		time.sleep(0.022)    # Read somewhere that 22ms is what the UI does.
		ser.setDTR(True)  # UP the DTR back

		self.init_time = time.time()

		time.sleep(2)
		pyfile = open(file, 'a')

		while(self.recording):
			if self.start_capture:
				self.start_capture = False
				ser.reset_input_buffer()
				pyfile.write('+++ Taking Capture\n')
			if self.end_capture:
				self.end_capture = False
				pyfile.write('--- Ending Capture\n')
				self.debug = False
				
			line = ser.readline()
			if line:
				string = line.decode()
				num = (string).strip('\n\r').split(", ")
				if(len(num) == 4):
					cap = Capture(float(num[0])/1000 + time.time(), num[1], num[2], num[3])
					if self.debug:
						self.debug -= 1
						print("val", str(cap))
						if not self.debug:
							self.end_capture = True
					pyfile.write(str(cap))
			
		ser.close()

	# starts longterm recording. note: you do not have to call this unless you stopped recording.
	def duino_start(self):
		self.recording = True
		self.sensorthread = threading.Thread(target=self.duino, args=())
		self.sensorthread.start()

	# stops recording, closes serial, and ends thread
	# add to deconstructor when implemented
	def duino_stop(self):
		self.recording = False
		self.sensorthread.join()

	# debug requires a number, if enabled it'll run until debug hits 0:
	# when it does, it stops capture.
	# can also set it so it will run for a certain duration instead
	def duino_capture(self, debug=0):
		self.start_capture = True
		self.debug = debug
		while(self.debug):
			sys.stdout.flush()

	def duino_stopcap(self):
		self.end_capture = True


if __name__ == '__main__':
	debug = True
	cam = camera()
	if "down" in str(sys.argv):
		cam.take(opfile="download.txt", debug=debug)
	else:
		cam.take(debug=debug)
	pass

