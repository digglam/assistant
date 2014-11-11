'''

Resetting the Gado robot via serial port

@author: Agusti Pellicer (Aalto University)

'''

import serial
ser = serial.Serial()
ser.port='/dev/ttyACM0'
ser.baudrate=1200
ser.open()
ser.close()