'''

A class for the main control loop for the Gado robot UI

@author: Agusti Pellicer (Aalto University)

'''

import wx
import robotThreading
import gadoDB

import Queue
import subprocess
from wx.lib.pubsub import Publisher

import os

import ThumbnailCtrl as TC

class GadoMain(wx.Frame):
	
	def __init__(self):
	    wx.Frame.__init__(self, None, wx.ID_ANY, "GadoUI", size=(640,550))
	
		#We create a queue to send messages to the robothread
	    self.q = Queue.Queue()

		#We create references to the panels
	    self.gadoStart = GadoStart(self,self.q)
	    self.gadoProcess = GadoProcess(self,self.q)
	    self.gadoEnd = GadoFinal(self,self.q)
	    self.gadoProcess.Hide()
	    self.gadoEnd.Hide()

	    self.sizer = wx.BoxSizer(wx.VERTICAL)
	    self.sizer.Add(self.gadoStart, 1, wx.EXPAND)
	    self.sizer.Add(self.gadoProcess, 1, wx.EXPAND)
	    self.sizer.Add(self.gadoEnd,1,wx.EXPAND)
	    self.SetSizer(self.sizer)
	
	    self.statusBar = self.CreateStatusBar()
	    self.statusBar.SetStatusText('Connecting to Gado')

	    #A reference for the next panel
	    self.gadoStart.processPanel = self.gadoProcess
	    self.gadoProcess.endPanel = self.gadoEnd
	    self.gadoEnd.startPanel = self.gadoStart

	    #So the panel can write in the statusBar
	    self.gadoProcess.statusBar = self.statusBar

	    #Create pub/sub
	    Publisher().subscribe(self.updateUI, "update")
	    #RobotThread!
	    self.robotThread = robotThreading.RobotThread(self.q)
	    self.robotThread.start()

	    #This means connect to the robot
	    self.q.put(('c',''))
		#Now we can put some stuff on the queue
	    self.Bind(wx.EVT_CLOSE, self.OnClose)
	    self.Show()
	def updateUI(self,msg):
		message = msg.data
		self.statusBar.SetStatusText(message)
	def OnClose(self,event):
		dlg = wx.MessageDialog(self,
		    "Do you really want to close this application? The robot is still runinng",
		    "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		result = dlg.ShowModal()
		dlg.Destroy()
		if result == wx.ID_OK:
			#This means quit the thing
			self.q.put(('q',''))
			self.Destroy()

class GadoStart(wx.Panel):
	""" Main panel to set up the run """
	def __init__(self, parent, queue):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.q = queue

 		#Sizers
 		self.vbox = wx.BoxSizer(wx.VERTICAL)
 		self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)

 		self.directoryLabel = wx.StaticText(self, label="Please choose a directory to save the scan artifacts:")


 		self.directoryText = wx.TextCtrl(self,style=wx.TE_READONLY)
		self.dirDialogButton = wx.Button(self, label="Choose directory")
		self.dirDialogButton.Bind(wx.EVT_BUTTON, self.showDirDialog)

		#First line
		self.hbox1.Add(self.directoryLabel, flag=wx.RIGHT, border=8)

		#Second line
		self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.hbox2.Add(self.directoryText, proportion=1, flag=wx.EXPAND)
		self.hbox2.Add(self.dirDialogButton)

		#Third line
		self.hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		self.tagsLabel = wx.StaticText(self, label="Tag this run")
		self.hbox3.Add(self.tagsLabel)
		#Fourth line
		self.hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		self.tagText = wx.TextCtrl(self)
		self.hbox4.Add(self.tagText, proportion=1, flag=wx.EXPAND)

		#Fifth line
		self.hbox5 = wx.BoxSizer(wx.HORIZONTAL)
		self.tagList = wx.ListCtrl(self,size=(-1, 300),style=wx.LC_REPORT|wx.BORDER_SUNKEN)
		self.tagList.InsertColumn(0, 'Tag')
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.addTag, self.tagList)
		self.populateTagList()
		self.hbox5.Add(self.tagList, proportion=1 ,flag=wx.CENTER|wx.EXPAND)
		#Fifth line
		self.hbox6 = wx.BoxSizer(wx.HORIZONTAL)
		self.startButton = wx.Button(self, label="Start!")
		self.startButton.Bind(wx.EVT_BUTTON, self.startProcess)
		self.startButton.Disable()

		Publisher().subscribe(self.enableButton, "connected")

		self.hbox6.Add(self.startButton, flag=wx.CENTER)
		#Adding the stuff
		self.vbox.Add(self.hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)		
		self.vbox.Add(self.hbox2, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		self.vbox.Add(self.hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		self.vbox.Add(self.hbox4, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		self.vbox.Add((-1, 10))
		self.vbox.Add(self.hbox5, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		self.vbox.Add((-1, 10))
		self.vbox.Add(self.hbox6, flag=wx.EXPAND|wx.CENTER, border=10)

		#Show the frame

		self.SetSizer(self.vbox)

	def enableButton(self,msg):
		self.startButton.Enable()
	def addTag(self, event):
		""" Adds a tag from the ListCtrl (list of tags) to the TextCtrl (user input)"""
		tag = event.GetText()
		if self.tagText.IsEmpty():
			self.tagText.SetValue(tag +',')
		else:
			text = self.tagText.GetValue().strip()
			if text[-1] == ',':
				self.tagText.SetValue(text + tag + ',')
			else:
				self.tagText.SetValue(text + ',' + tag + ',')

	def populateTagList(self):
		""" Connects to the database to fill ListCtrl """
		db = gadoDB.GadoDB('gado.db')
		tags = db.getTags()
		db.closeDB()
		index = 0
		for tag_id, tag in tags:
			self.tagList.InsertStringItem(index, tag)
			index = index + 1

		self.tagList.SetColumnWidth(0,wx.LIST_AUTOSIZE)
	def showDirDialog(self, event):
		""" Shows the directory dialog and fills the TextCtrl """
		self.dirDialog = wx.DirDialog(self, "Choose a directory to save the pictures")
		if self.dirDialog.ShowModal() == wx.ID_OK:
			self.directoryText.SetValue(self.dirDialog.GetPath())
		self.path = self.dirDialog.GetPath()
		#Share the path
		self.processPanel.path = self.path
		
		self.dirDialog.Destroy()
	def startProcess(self, event):
		""" Insert the tags to the database and starts the main process of the Gado """

		# 'parsing' the tags
		tags = self.tagText.GetValue().strip()
		if not tags:
			dlg = wx.MessageDialog(self,
			    "You need to put some tags",
			    "Tags missing", wx.OK)
			result = dlg.ShowModal()
			dlg.Destroy()
			return
		if not self.directoryText.GetValue():
			dlg = wx.MessageDialog(self,
			    "You need to choose a directory",
			    "Directory missing", wx.OK)
			result = dlg.ShowModal()
			dlg.Destroy()
			return
		if tags[-1] == ',':
			tags = tags[:-1].split(',')
		else:
			tags = tags.split(',')
		#just removing whitespaces
		tags = [x.strip() for x in tags]
		self.q.put(('t',tags))
		#Db stuff
		db = gadoDB.GadoDB('gado.db')
		tags = db.insertTags(tags)
		db.closeDB()
		#Hide the panel and show the right one
		self.Hide()
		self.processPanel.timer.Start(100)
		self.processPanel.thumbImages.ShowDir(self.path)
		self.processPanel.Show()
		self.parent.Layout()
		#Run the robot with the path to save the pictures
		self.q.put(('r',self.directoryText.GetValue()))
		

class GadoProcess(wx.Panel):
	def __init__(self, parent,queue):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.vboxp = wx.BoxSizer(wx.VERTICAL)
		self.hbox1p = wx.BoxSizer(wx.HORIZONTAL)

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER,self.updateProgressBar,self.timer)
		self.progressLabel = wx.StaticText(self, label="Genius working ")
		self.numberDoneLabel = wx.StaticText(self,label="0")
		self.hbox1p.Add(self.progressLabel, flag=wx.CENTER|wx.EXPAND, border=8)
		self.hbox1p.Add(self.numberDoneLabel, flag=wx.CENTER|wx.EXPAND, border=8)

		self.hbox2p = wx.BoxSizer(wx.HORIZONTAL)
		self.progressBar = wx.Gauge(self, style=wx.GA_SMOOTH)
		self.progressBar.SetValue(50)
		self.hbox2p.Add(self.progressBar, proportion=1, flag=wx.EXPAND)


		self.hbox3p = wx.BoxSizer(wx.HORIZONTAL)
		self.thumbImages = TC.ThumbnailCtrl(self,-1,size=(640,350))
		self.hbox3p.Add(self.thumbImages, proportion=1,flag=wx.EXPAND)
		self.thumbImages.ShowFileNames()
		self.thumbImages.Bind(TC.EVT_THUMBNAILS_DCLICK, self.openImage)

		self.vboxp.Add(self.hbox1p,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		self.vboxp.Add((-1, 10))
		self.vboxp.Add(self.hbox2p,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		self.vboxp.Add((-1, 10))
		self.vboxp.Add(self.hbox3p,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		
		Publisher().subscribe(self.gadoEnd, "end")
		Publisher().subscribe(self.gadoIteration, "iteration")
		self.SetSizer(self.vboxp)

	def openImage(self,event):
		subprocess.Popen(['xdg-open', self.thumbImages.GetItem(self.thumbImages.GetSelection())._dir])

	def gadoEnd(self,msg):
		message = msg.data -1
		print message
		print str(message)
		self.Hide()
		#Put 0 again
		self.numberDoneLabel.SetLabel(str(0))
		self.timer.Stop()
		self.endPanel.numberLabel.SetLabel(str(message))
		self.endPanel.Show()
		self.parent.Layout()

	def updateProgressBar(self,event):
		self.progressBar.Pulse()
	def gadoIteration(self,msg):
		message = msg.data
		self.numberDoneLabel.SetLabel(str(msg.data))
		self.thumbImages.ShowDir(self.path)

class GadoFinal(wx.Panel):
	def __init__(self,parent,queue):
		wx.Panel.__init__(self,parent)
		self.parent = parent
		self.vboxf = wx.BoxSizer(wx.VERTICAL)
		self.hbox1f = wx.BoxSizer(wx.HORIZONTAL)

		self.endLabel = wx.StaticText(self, label="End of the run")

		self.hbox1f.Add(self.endLabel, flag=wx.CENTER|wx.EXPAND, border=8)

		self.hbox2f = wx.BoxSizer(wx.HORIZONTAL)
		self.iterationLabel = wx.StaticText(self,label="Scanned artifacts:")
		self.numberLabel = wx.StaticText(self,label="0")

		self.hbox2f.Add(self.iterationLabel)
		self.hbox2f.Add(self.numberLabel)


		self.hbox3f = wx.BoxSizer(wx.HORIZONTAL)
		self.restartButton = wx.Button(self,label="Make a new run!")
		self.hbox3f.Add(self.restartButton)
		self.restartButton.Bind(wx.EVT_BUTTON, self.restartGado)

		self.showDirectoryButton = wx.Button(self, label="Open directory")
		self.showDirectoryButton.Bind(wx.EVT_BUTTON,self.openDirectory)
		self.hbox3f.Add(self.showDirectoryButton)

		self.vboxf.Add(self.hbox1f,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		self.vboxf.Add((-1, 10))
		self.vboxf.Add(self.hbox2f,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		self.vboxf.Add((-1, 10))
		self.vboxf.Add(self.hbox3f,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

		self.SetSizer(self.vboxf)

	def openDirectory(self,event):
		#We open the file manager
		subprocess.Popen(['xdg-open', self.startPanel.path])
	def restartGado(self,event):
		#We go to the first panel
		self.Hide()
		self.startPanel.Show()
		self.parent.Layout()

if __name__ == '__main__':
	app = wx.App()
	frame = GadoMain()
	app.MainLoop()