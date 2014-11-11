'''
    
Collecting the energy readings
    
@author: Agusti Pellicer (Aalto University)
    
'''

import energyDB
from datetime import datetime
import time
import plugwise

# The addresses of our Plugwise energy monitors
CIRCLE_PLUS_MAC = "000D6F0000729887"
CIRCLE_MAC_1 = "000D6F0000B81CC1"
CIRCLE_MAC_2 = "000D6F00029C2AD3"
CIRCLE_MAC_3 = "000D6F0003562C67"
CIRCLE_MAC_4 = "000D6F0003562DA5"

#STICK = "/dev/tty.usbserial-A700dr5f"
STICK = "/dev/ttyUSB0"
DEVICES_MAC = [CIRCLE_PLUS_MAC, CIRCLE_MAC_1, CIRCLE_MAC_2, CIRCLE_MAC_3, CIRCLE_MAC_4]


def collectReadings(device):
	global db
	try:
		power = device.get_power_usage()
		timestamp = datetime.now().isoformat()
		db.insertReading(device.mac, power, timestamp,"")
		print device.mac + " : " + str(power) + " at " + timestamp
	except ValueError:
		print "Failed reading " + device.mac

#Init the stick and the devices
stick = plugwise.Stick(STICK)
devices = [plugwise.Circle(circle, stick) for circle in DEVICES_MAC]

db = energyDB.EnergyDB("energy.db")

#Start collecting energy readings
while True:
	print "##########################################"
	for device in devices:
		collectReadings(device)
		time.sleep(5)
	print "##########################################"


