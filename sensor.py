
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
	def __init__(self):
		# arduino globals
		self.start_capture = False
		self.end_capture = False
		self.recording = False
		self.debug = 0

	def duino(self, file):
		# port is a device name: depending on operating system. e.g. /dev/ttyUSB0 on GNU/Linux or COM3 on Windows.
		# Add compatibility for linux and windows
		import serial
		# ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
		ser = serial.Serial('COM3', 9600, timeout=1)
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
				# pyfile.write('+++ Taking Capture\n')
			if self.end_capture:
				self.end_capture = False
				# pyfile.write('--- Ending Capture\n')
				self.debug = False
				
			line = ser.readline()
			try:
				string = line.decode()
				num = (string).strip('\n\r').split(", ")
				if(len(num) == 4):
					# cap = Capture(float(num[0])/1000 + time.time(), num[1], num[2], num[3])
					cap = Capture(time.time(), num[1], num[2], num[3])
					if self.debug:
						self.debug -= 1
						print("val", str(cap))
						if not self.debug:
							self.end_capture = True
					pyfile.write(str(cap))
					pyfile.write("\n")
			except:
				continue
			
		pyfile.close()
		ser.close()

	# starts longterm recording. note: you do not have to call this unless you stopped recording.
	def start(self, file="run.txt"):
		if not self.recording:
			self.recording = True
			self.sensorthread = threading.Thread(target=self.duino, args=(file, ))
			self.sensorthread.start()

	# stops recording, closes serial, and ends thread
	# add to deconstructor when implemented
	def stop(self):
		if self.recording:
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

# returns a list of captures from file
def read_sensor_data(file):
	with open(file, 'r') as pyfile:
		out = []
		for string in iter(pyfile.readline, ''):
			num = (string).strip('\n\r').split(", ")
			if(len(num) == 4):
				out.append(Capture(num[0], num[1], num[2], num[3]))
	return out

# gets list of list of capture objects, head list is for each cam capture
def get_captures(file):
	with open(file, 'r') as pyfile:
		in_cap = False
		out = []
		sub_list = []
		for string in iter(pyfile.readline, ''):
			if in_cap: # currently capturing, scanning for capture or stopcap
				num = (string).strip('\n\r').split(", ")
				if(string[0] == '-'):
					out.append(sub_list)
					sub_list = []
					in_cap = False
				elif(len(num) == 4):
					sub_list.append(Capture(num[0], num[1], num[2], num[3]))
			elif(string[0] == '+'): # not capturing, scanning for startcap
				in_cap = True
	return out

def ex_sensor():
	caps = get_captures("experiments/ex_sensor.txt")
	# get first reading of first capture
	reading = caps[0][0]
	print("Time (s): " + reading.time + ", X_Tilt: " + reading.x_tilt + ", Y_Tilt: " + reading.y_tilt + ", Z_Tilt: " + reading.z_tilt)

	# read_sensor_data will instead of getting captures, just give a continuous list of all readings
	# might be more compatible with current functionality iirc

if __name__ == '__main__':
	s = Sensor()
	s.start()
	time.sleep(10)
	s.stop()