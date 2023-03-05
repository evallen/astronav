
#python - install --upgrade pip
import serial #python -m pip install -U pyserial
import time
import threading
import time




class sensor:
	def __init__(self, debug=False):
		self.sensorthread = threading.Thread(target=self.duino, args=())
		self.stop = False
		self.debug = debug

		# modify this to run constantly polling and storing arduino data, but use 
	def duino(self, file='output.txt', iter=50):
		# port is a device name: depending on operating system. e.g. /dev/ttyUSB0 on GNU/Linux or COM3 on Windows.
		# Add compatibility for linux and windows
		ser = serial.Serial('COM3', 9800, timeout=1)
		time.sleep(2)
		pyfile = open(file, 'a')

		#if debug: for i in range(iter):
		while True:
			line = ser.readline()
			if line:
				string = line.decode()
				timestamp = str(time.time())
				num = (string).rstrip()
				if b"Reading" not in line:
					if self.debug:
						print("\tval:", num, end='')
						print("\ttime:", timestamp)
						pyfile.write(num + ' ' + timestamp + '\n')
			if self.stop:
				break
		self.stop = False
		ser.close()

	def startRecord(self):
		self.sensorthread.start()
	
	def stopRecord(self):
		self.stop = True
		self.sensorthread.join()


if __name__ == '__main__':
	s = sensor()
	s.startRecord()
	time.sleep(10)
	s.stopRecord()