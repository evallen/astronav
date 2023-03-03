
#python - install --upgrade pip
import serial #python -m pip install -U pyserial
import time

class sensor:

    	# modify this to run constantly polling and storing arduino data, but use 
	def duino(self, file='output.txt', iter=50, debug=False):
		# port is a device name: depending on operating system. e.g. /dev/ttyUSB0 on GNU/Linux or COM3 on Windows.
		# Add compatibility for linux and windows
		ser = serial.Serial('COM3', 9800, timeout=1)
		time.sleep(2)
		pyfile = open(file, 'a')

		#while True:
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
    s = sensor()
    s.duino()