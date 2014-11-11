'''

An example of reading Plugwise energy monitors
@author: Agusti Pellicer (Aalto University)

'''

import plugwise
import time


# Addresses of our CIRCLES
# N's CIRCLES
CIRCLE_PLUS_MAC_2 = "000D6F00036BB2F0"
CIRCLE_MAC_2 = "000D6F00029C2AD3"
#J'S CIRCLES
CIRCLE_PLUS_MAC = "000D6F0000729887"
CIRCLE_MAC_1 = "000D6F0000B81CC1"
#N'S CIRCLES
CIRCLE_MAC_3 = "000D6F0003562C67"
CIRCLE_MAC_4 = "000D6F0003562DA5"


#STICK = "/dev/tty.usbserial-A700dr5f"
STICK = "/dev/ttyUSB0"
#DEVICES_MAC = [CIRCLE_PLUS_MAC, CIRCLE_MAC_1, CIRCLE_MAC_2, CIRCLE_MAC_3, CIRCLE_MAC_4]
DEVICES_MAC = [CIRCLE_PLUS_MAC, CIRCLE_MAC_1, CIRCLE_MAC_3, CIRCLE_MAC_4]

stick = plugwise.Stick(STICK)
devices = [plugwise.Circle(circle, stick) for circle in DEVICES_MAC]

for device in devices:
	print device.get_power_usage()
	time.sleep(2)
