'''

A class for robot threading

@author: Agusti Pellicer (Aalto University)

'''

import Gado_2.ScannerControl.ScannerFunctions as SF
import Gado_2.CameraControl.CameraFunctions as CF
import Gado_2.ComputerVision.BarcodeDetection as B

import Gado_2.Robot as Robot
import time
from datetime import datetime

import os
import sane
import sys
import threading

import gadoDB
import Queue

from wx.lib.pubsub import Publisher

from PIL import Image
import wx

class RobotThread(threading.Thread):
	def __init__(self, queue):
		""" We got access to the shared queue and the statusBar in the GUI to write status """
		threading.Thread.__init__(self)
		self.q = queue

	def gadoIteration(self,path,run):
		""" An iteration of the robot, we need the path to save the pictures and a timestamp to identify the run """

		#We take a picture to see if we can find the QR code
		nameFile = path + '/' + datetime.now().isoformat()
		self.camera.captureBackImage(nameFile +"-cam.jpg")
		#Try to see if we find the QR code
		barcodes = B.findBarcodes(nameFile +"-cam.jpg")
		print barcodes
		if barcodes:
		    if barcodes[0] and barcodes[0] == "project gado":
		        self.gado.sendRawActuatorWithBlocking(25)
		        print "--------"
		        print "DONE WITH STACK"
		        print "--------"
		        #Time to close everyhting we opened
		        #self.exitRobot()
		        return True
		#1
		self.gado.sendRawArmTimeBlocking(0)
		start = time.time()
		print '1'
		# #2
		self.gado.sendVacuum(140)
		print '2.1'
		self.gado.lowerAndLiftInternal()
		print '2.2'
		self.gado.sendRawActuatorWithBlocking(70)
		
		print '2.4'
		# #3
		self.gado.sendRawArmTimeBlocking(80)
		print '3'
		# #4
		#self.gado.sendRawActuatorWithBlocking(80)
		#self.gado.sendVacuum(0)
		#self.gado.sendRawActuatorWithBlocking(60)

		print '4'
		self.gado.sendRawActuatorWithBlocking(140)
		#Save scanned image
		image = self.scanner.scanImage()
		
		image.save(nameFile + '.tiff')
		#Save the thumbnail in png format
		image.thumbnail((700,500), Image.ANTIALIAS)
		image.save(nameFile + '-t.png')

		#self.gado.sendVacuum(200)
		#self.gado.lowerAndLiftInternal()

		#We save it to the the db
		db = gadoDB.GadoDB('gado.db')
		tags = db.insertArtifact(nameFile,run,self.tags)
		db.closeDB()

		#Some error problem maybe
		if not os.path.exists(nameFile + '.tiff'):
		    print "The scanner failed to take an image"
		    self.gado.sendVacuum(0)
		    self.gado.sendRawActuatorWithBlocking(50)
		    return False
		#6
		print '6'
		self.gado.sendRawActuatorWithBlocking(70)
		
		#7
		print '7'
		self.gado.sendRawArmTimeBlocking(160)
		self.gado.sendVacuum(0)
		time.sleep(2)
		elapsed = time.time() - start
		#elapsed = elapsed - 5
		print elapsed

	def connectToDevices(self):
		""" Connect to the devices we use: robot, camera and scanner """
		#Setting up the robot
		self.gado = Robot.Robot('/dev/ttyACM0')

		time.sleep(5)
		self.gado.connect()

		self.gado.goHome()
 		#Our own scanner and camera
 		self.scanner = SF.Scanner()
 		self.camera = CF.Camera(camera=1,resolution=(640,480))

 	def exitRobot(self):
 		""" We close the scanner and the camera """
 		self.scanner.closeScanner()
 		self.camera.closeCamera()
 		

 	def gadoProcess(self,path):
 		""" Main loop """
 		iteration = 0
 		run = datetime.now().isoformat()
 		while True:
 		    finished = self.gadoIteration(path,run)
 		    first_run = 0
 		    iteration = iteration + 1
 		    wx.CallAfter(Publisher().sendMessage, "iteration", iteration)
 		    if finished:
 		    	return iteration
 		    if finished == False:
 		    	#An error has ocurred in the iteration
 		    	return iteration

 	def readMessage(self,message):
 		""" We read the messages the robot receives """ 
 		print message
 		code, arguments = message
 		# Connect to the robot
 		if code == 'c':
 			self.connectToDevices()
 			#We send the updates to the UI
 			wx.CallAfter(Publisher().sendMessage, "update", "Connected to Gado")
 			wx.CallAfter(Publisher().sendMessage, "connected", "Connected to Gado")
 		# Run the robot
 		if code == 'r':
 			#We send an update to the UI
 			wx.CallAfter(Publisher().sendMessage, "update", "Running Gado")
 			self.pathImages = arguments
 			nIterations = 6
 			nIterations = self.gadoProcess(self.pathImages)
 			#Updates to the UI
 			wx.CallAfter(Publisher().sendMessage, "update", "Gado finished")
 			wx.CallAfter(Publisher().sendMessage, "end", nIterations)
 		# Set the tags we are using for this run
 		if code == 't':
 			self.tags = arguments
 		# Robot exit
 		if code == 'q':
 			sys.exit()

	def run(self):
		""" Loop for reading the messages that are send to the robot """
		while True:
			try:  
				obj = self.q.get(True)
				self.readMessage(obj)  
			except Queue.Empty:  
				pass
			