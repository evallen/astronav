
#python - install --upgrade pip
import serial #python -m pip install -U pyserial
import time
import threading
import time
import sys

# simple capture object for csv grabbing
class Capture:
	def __init__(self, time, x_tilt, y_tilt, z_tilt):
		self.time = time; self.x_tilt = x_tilt
		self.y_tilt = y_tilt; self.z_tilt = z_tilt
	def __str__(self):
		return (str(self.time) + ", " + str(self.x_tilt) + ", " + 
				str(self.y_tilt) + ", " + str(self.z_tilt))

class Sensor:
	def __init__(self, file='output.txt'):
		# arduino globals
		self.start_capture = False
		self.end_capture = False
		self.recording = False
		self.debug = 0
		self.file = file

	def duino(self):
		# port is a device name: depending on operating system. e.g. /dev/ttyUSB0 on GNU/Linux or COM3 on Windows.
		# Add compatibility for linux and windows
		import serial
		ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
		ser.setDTR(False) # Drop DTR
		time.sleep(0.022)    # Read somewhere that 22ms is what the UI does.
		ser.setDTR(True)  # UP the DTR back

		self.init_time = time.time()

		time.sleep(2)
		pyfile = open(self.file, 'a')

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
					pyfile.write("\n")
			
		pyfile.close()
		ser.close()

	# starts longterm recording. note: you do not have to call this unless you stopped recording.
	def start(self):
		self.recording = True
		self.sensorthread = threading.Thread(target=self.duino, args=())
		self.sensorthread.start()

	# stops recording, closes serial, and ends thread
	# add to deconstructor when implemented
	def stop(self):
		self.recording = False
		self.sensorthread.join()

	# debug requires a number, if enabled it'll run until debug hits 0:
	# when it does, it stops capture.
	# can also set it so it will run for a certain duration instead
	def capture(self, debug=0):
		self.start_capture = True
		self.debug = debug
		while(self.debug):
			sys.stdout.flush()

	def stopcap(self):
		self.end_capture = True

	def change_file(self, file):
		self.stop()
		self.file = file
		self.start()


if __name__ == '__main__':
	s = Sensor()
	s.start()
	time.sleep(10)
	s.stop()