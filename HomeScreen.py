#Test File, free to adjust as needed

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import *
from kivy.core.window import Window
from kivy.uix.progressbar import ProgressBar
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.properties import StringProperty
from kivy.clock import Clock
from pprint import pprint

from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from CameraTools import CameraTools

import threading
import time
import json

from CameraTools import CameraTools
#import cncmain3

#cncmain3.init()

#### cncmain3 initializations starts ####

from pynput.keyboard import Key, Listener
#import curses
import atexit
import RPi.GPIO as GPIO
import pickle
import os
import json

kit = MotorKit()

kit.stepper1.release()
kit.stepper2.release()


Enc_Ax = 4  				# Encoder input A: input GPIO 4 
Enc_Bx = 17  			        # Encoder input B: input GPIO 17 
Enc_Ay = 18
Enc_By = 27
LimitInx = 22
LimitIny = 23

LockRotary = threading.Lock()		# create lock for rotary switch

x_pos = 1000
y_pos = 1000  			# Start counting from 0
Current_Ax = 1					# Assume that rotary switch is not 
Current_Bx = 1					# moving while we init software
Current_Ay = 1
Current_By = 1

speed = 1
calix = [1000, 1000, 1000]
caliy = [1000, 1000, 1000]

savedx = []
savedy = []
nodeArray = []

controlBin = False

ctools = CameraTools()
#### cncmain3 initializations end ####

#### cncmain3 functions start ####

def cncinit():
	global savedx, savedy, nodeArray

	GPIO.setwarnings(True)
	GPIO.setmode(GPIO.BCM)					# Use BCM mode
											# define the Encoder switch inputs
	GPIO.setup(Enc_Ax, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 				
	GPIO.setup(Enc_Bx, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(Enc_Ay, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 				
	GPIO.setup(Enc_By, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(LimitInx, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.setup(LimitIny, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	while GPIO.input(LimitInx) == False:
		kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
	while GPIO.input(LimitIny) == False:
		kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)

	for i in range(20):
		kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
	for i in range(20):
		kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)	

	x_pos = 1000
	y_pos = 1000		
											# setup callback thread for the A and B encoder 
											# use interrupts for all inputs
	GPIO.add_event_detect(Enc_Ax, GPIO.RISING, callback=rotary_interrupt_x) 				# NO bouncetime 
	GPIO.add_event_detect(Enc_Bx, GPIO.RISING, callback=rotary_interrupt_x) 				# NO bouncetime
	
	GPIO.add_event_detect(Enc_Ay, GPIO.RISING, callback=rotary_interrupt_y) 				# NO bouncetime 
	GPIO.add_event_detect(Enc_By, GPIO.RISING, callback=rotary_interrupt_y) 				# NO bouncetime 

	saved = getLocations()
	if saved is None:
		savedx = []
		savedy = []
	else:
		locs = list(zip(*saved))
		savedx = locs[0]
		savedy = locs[1]	

	nodeArray = readConfig('nodeInfo.dat')['data']
	#nodeArray = [item for sublist in config for item in sublist]


	return
	
#interrupt function x location
def rotary_interrupt_x(A_or_B):
	global x_pos, Current_Ax, Current_Bx, LockRotary
													# read both of the switches
	Switch_A = GPIO.input(Enc_Ax)
	Switch_B = GPIO.input(Enc_Bx)
													# now check if state of A or B has changed
													# if not that means that bouncing caused it
	if Current_Ax == Switch_A and Current_Bx == Switch_B:		# Same interrupt as before (Bouncing)?
		return										# ignore interrupt!

	Current_Ax = Switch_A								# remember new state
	Current_Bx = Switch_B								# for next bouncing check


	if (Switch_A and Switch_B):						# Both one active? Yes -> end of sequence
		LockRotary.acquire(blocking=True, timeout=1)						# get lock 
		if A_or_B == Enc_Bx:							# Turning direction depends on 
			x_pos += 1						# which input gave last interrupt
		else:										# so depending on direction either
			x_pos -= 1						# increase or decrease counter
		LockRotary.release()						# and release lock
	return	
	
#interrupt function y location
def rotary_interrupt_y(A_or_B):
	global y_pos, Current_Ay, Current_By, LockRotary
													# read both of the switches
	Switch_A = GPIO.input(Enc_Ay)
	Switch_B = GPIO.input(Enc_By)
													# now check if state of A or B has changed
													# if not that means that bouncing caused it
	if Current_Ay == Switch_A and Current_By == Switch_B:		# Same interrupt as before (Bouncing)?
		return										# ignore interrupt!

	Current_Ay = Switch_A								# remember new state
	Current_By = Switch_B								# for next bouncing check


	if (Switch_A and Switch_B):						# Both one active? Yes -> end of sequence
		LockRotary.acquire(blocking=True, timeout=1)						# get lock 
		if A_or_B == Enc_By:							# Turning direction depends on 
			y_pos -= 1						# which input gave last interrupt
		else:										# so depending on direction either
			y_pos += 1						# increase or decrease counter
		LockRotary.release()						# and release lock
	return	

def rehome():
	global x_pos, y_pos
	while GPIO.input(LimitInx) == False:
		kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
	while GPIO.input(LimitIny) == False:
		kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)	

	for i in range(50):
		kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
	for i in range(50):
		kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
	x_pos = 1000
	y_pos = 1000
	
	return
	

def readConfig(filename):
	with open(filename) as file:
		config = json.load(file)
	return config

def demomove(xloc, yloc, self):
	if xloc >= 24350 or xloc <= 1000:
		return
	if yloc >= 9760 or yloc <= 1000:
		return
	global x_pos, y_pos
	while x_pos <= (xloc - 250):
		kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	
	while x_pos <= (xloc - 8):
		kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
		time.sleep(.005)
	
	#x positioning, left
	while x_pos >= (xloc + 250):
		kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
		time.sleep(.005)
		
	while x_pos>= (xloc + 8):
		kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
		time.sleep(.005)	

	#y positioning, Forward
	while y_pos <= (yloc - 250):
		kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
		time.sleep(.005)		

	
	while y_pos <= (yloc - 8):
		kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
		time.sleep(.005)

	#y positioning, Backward
	while y_pos >= (yloc + 250):
		kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	
	while y_pos >= (yloc + 8):
		kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
		time.sleep(.005)

	#time.sleep(.5)
	#homeScreen.showWebcamFeed
	self.cameraTools.recordNode(self.nodeQueue[0], self.numberOfRecordings, self.recordingTime, self.fps, self.timeBetweenImages)
	#self.changeActiveNode()

def moveRight():
	print ("RIGHT")
	for i in range (speed):
		kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	#screen.clear()

def moveLeft():
	print ("LEFT")
	for i in range (speed):
		kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	#screen.clear()

def moveForward():
	print ("FORDWARD")
	for i in range (speed):
		kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	#screen.clear()

def moveBackwards():
	print ("BACKWARDS")
	for i in range (speed):
		kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	#screen.clear()

def speedUp():
	global speed
	print ("Speed up")
	speed = (speed * 5)
	if speed == 625:
		#screen.clear()
		print("Maximum speed")
		time.sleep(1)
	time.sleep(1)
	#screen.clear()

def speedDown():
	global speed
	print ("Speed down")
	speed = (speed // 5)
	if speed == 1:
		#screen.clear()
		print("Minimum speed")
		time.sleep(1)
	time.sleep(1)
	#screen.clear()

def printLocations():
	print ("Current X = ", x_pos)
	print ("Current Y = ", y_pos)
	
	#savedlength = len(savedx)
	print("Saved locations:")
	for i in range(0,4):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	#screen.clear()
	for i in range(4,8):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	#screen.clear()
	for i in range(8,12):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	#screen.clear()
	for i in range(12,16):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	#screen.clear()
	for i in range(16,20):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	#screen.clear()

def populate():
	global savedx, savedy

	savedx = []
	savedy = []
	savedx.append(calix[0])
	savedy.append(caliy[0])

	for i in range(1, 8):
		savedx.append(savedx[i-1] + (calix[1] - calix[0]))
		savedy.append(caliy[0])
	savedx.append(calix[0])
	savedy.append(caliy[0] + (caliy[2] - caliy[0]))

	for i in range(9, 16):
		savedx.append(savedx[i-1] + (calix[1] - calix[0]))
		savedy.append(savedy[8])
	savedx.append(calix[0])
	savedy.append(caliy[0] + ((caliy[2] - caliy[0]) * 2))

	for i in range(17, 24):
		savedx.append(savedx[i-1] + (calix[1] - calix[0]))
		savedy.append(savedy[16])
	savedx.append(calix[0])
	savedy.append(caliy[0] + ((caliy[2] - caliy[0]) * 3))

	for i in range(25, 32):
		savedx.append(savedx[i-1] + (calix[1] - calix[0]))
		savedy.append(savedy[24])
	savedx.append(calix[0])
	savedy.append(caliy[0] + ((caliy[2] - caliy[0]) * 4))

	for i in range(33, 40):
		savedx.append(savedx[i-1] + (calix[1] - calix[0]))
		savedy.append(savedy[32])
	savedx.append(calix[0])
	savedy.append(caliy[0] + ((caliy[2] - caliy[0]) * 5))

	for i in range(41, 48):
		savedx.append(savedx[i-1] + (calix[1] - calix[0]))
		savedy.append(savedy[40])
	saveLocations()

def go(self):
	global savedx, savedy, nodeArray
	rehome()
	for i in range(len(savedx)):
		if nodeArray[i] == 1:
			print("Position: ", i+1)
			demomove(savedx[i], savedy[i], self)
			self.changeActiveNode
		#screen.clear()
		if (i+1)%8 == 0:
			rehome()
	#demomove(1000, 1000)
	print("DONE")

def saveLocations():
	global savedx, savedy
	locs = list(zip(savedx, savedy))
	with open("locData.dat", "wb") as fp:
		pickle.dump(locs, fp)

def readLocations():
	with open("locData.dat", "rb") as fp:
		locs = pickle.load(fp)
	return locs

def getLocations():
	if os.path.isfile("locData.dat"):
		return readLocations()
	else:
		return None

def keyControl(self):

	
	rehome()
	with Listener(
	on_press=on_press) as listener:
		listener.join()

	return

#main loop
def on_press(key):

	global x_pos, y_pos, nodeArray, controlBin
	
	keyp = str(key)
	
	#if controlBin == False:
		#return

	if keyp == str('\'q\''):
		return False
		#kit.stepper1.release()
		#kit.stepper2.release()
		#return False
		#print ("End Keyboard Control") 
		#time.sleep(.5)
		#break
	elif keyp == str('\'d\''):
		moveRight()
	elif keyp == str('\'a\''):
		moveLeft()
	elif keyp == str('\'w\''):
		moveForward()
	elif keyp == str('\'s\''):
		moveBackwards()

	# speeds up the motors so that
	# it is not a pain to move
	# across the machine
	elif (key == Key.page_up and speed <= 5):
		speedUp()

	elif (key == Key.page_down and speed >= 25):
		print ("Already at maximum speed")
	# slows down the motors to allow
	# for slow more precise movements
	elif (key == Key.page_down and speed >= 4):
		speedDown()
	elif (key == Key.page_down and speed <= 1):
		print ("Already at minimum speed")
		time.sleep(.5)
		#screen.clear()
			
	#print out locations
	elif keyp == str('\'l\''):
		printLocations()
				
				
	elif keyp == str('\'1\''):
		print ("Saved current location")
		calix[0] = x_pos
		caliy[0] = y_pos
		time.sleep(1)
		#screen.clear()
	elif keyp == str('\'2\''):
		print ("Saved current location")
		calix[1] = x_pos
		caliy[1] = y_pos
		time.sleep(.5)
		#screen.clear()
	elif keyp == str('\'3\''):
		print ("Saved current location")
		calix[2] = x_pos
		caliy[2] = y_pos
		time.sleep(.5)
		#screen.clear()
	elif keyp == str('\'g\''):
		populate()

				
	#elif keyp == str('\'g\''):
		#go()


	return
		
#### cncmain3 functions end ####

cncinit()

class Home(FloatLayout):

	def __init__(self):

		global nodeArray		

		super(Home, self).__init__()
		# Window.clearcolor = (1, 1, 1, 1)
		Window.size = (640, 480)
		#Window.borderless = True
		self.size = Window.size
		self.deviceArray = Widget(size=(100,100))
		self.add_widget(self.deviceArray)

		self.homeNodeArray = nodeArray
		self.fillQueue((8,6))
		self.setParameters()

		self.timeRemaining = 10
		self.startTime = time.time()
		self.started = False
		self.currentStatus = "Idle"

		self.addProgressbar()

		self.setNodeProperties()
		self.populateNodes(self.nodeSize)

		self.addCameraViewButton()
		self.addNodeIncrementButton()
		self.addSettingsButton()
		self.addStopButton()

		self.addStatusLabel()
		self.addTimeLeftLabel()
		self.addCameraPositionLabel()
		self.addTimeLeftValueLabel()
		self.addCurrentStatusLabel()

		self.cameraTools = CameraTools()

	def updateTimeRemaining(self, *args):
		if self.started:
			if self.webcamThread.isAlive():
				self.currentStatus = "Recording"
				self.timeLeftValueLabel.text = str(10-int(time.time() - self.startTime))
			else:
				self.currentStatus = "Idle"
				self.timeLeftValueLabel.text = str(10)

		if self.currentStatus == "Idle" and self.currentStatusLabel.text == "Recording":
			self.changeActiveNode3()

		if self.oldWidth is not Window.size[0]:
			self.deviceArray.canvas.clear()
			self.populateNodes(self.nodeSize)

		self.currentStatusLabel.text = self.currentStatus

	def createNode(self, xpos, ypos):
		return Line(rounded_rectangle=(xpos, ypos, Window.size[0] / 4 - 10, Window.size[1] / 2, 10))

	def populateNodes(self, size):
		with self.deviceArray.canvas:
			for rowNum in range(0,size[0]):
				for colNum in range(0, size[1]):
					currentNode = rowNum * size[1] + colNum
					if currentNode == self.activeNode:
						Color(1,0,0,1)
						self.recordingProgressBar.value = (currentNode / self.nodeCount) * 1000
					else:
						Color(1,1,1,1)
					self.oldWidth = Window.size[0]
					self.deviceArrayList.append(self.createNode(colNum * (Window.size[0] / 4) + 5, Window.size[1] / 2 - 10))
		self.addNodeLabels()
	
	def fillQueue(self, size):
		self.posArray = []
		posRowArray = []
		initChar = 'A'
		#initChar = chr(ord('A') + size[0])
		for rowNum in range(1, size[0] + 1):
			for colNum in range(1, size[0] + 1):
				posRowArray.append(str(chr(ord(initChar)) + str(rowNum)))
				initChar = chr(ord(initChar) + 1)
			self.posArray.append(posRowArray)
			posRowArray = []
			initChar = 'A'

		self.flatPosArray = [item for sublist in self.posArray for item in sublist]
		self.nodesStatusArray = list(zip(self.flatPosArray, self.homeNodeArray))
		self.nodeQueue = []
		for node in self.nodesStatusArray:
			if node[1] == 1:
				self.nodeQueue.append(node[0])
		self.recordedNodes = []
		print(self.nodeQueue)

	def changeActiveNode(self, instance):
		self.activeNode = self.activeNode + 1
		if self.activeNode >= self.nodeCount:
			self.activeNode = 0
		self.populateNodes(self.nodeSize)

	def changeActiveNode2(self):
		self.activeNode = self.activeNode + 1
		if self.activeNode >= self.nodeCount:
			self.activeNode = 0
		self.populateNodes(self.nodeSize)

	def changeActiveNode3(self):
		self.recordedNodes.append(self.nodeQueue.pop(0))
		for x in range(4):
			if len(self.nodeQueue) < 4:
				self.nodeQueue.append("")
		if self.nodeQueue[0] == "":
			self.fillQueue((8,6))
			
			
		for label in self.activeNodeLabels:
			label.canvas.clear()
		self.populateNodes(self.nodeSize)
		
	def showWebcamFeed(self, instance):
		self.started = True
		self.startTime = time.time()
		self.webcamThread = WebcamThread(1, self.nodeQueue[0], self.cameraTools, self.recordingTime, self.numberOfRecordings, self.framesPerSecond, self.timeBetweenImages)		
		self.webcamThread.start()

	def showWebcamFeed2(self, instance):
		webcamThread = WebcamThread(1, "CameraThread")
		webcamThread.start()
		#WebcamTest2.show_webcam()

	def setNodeProperties(self):
		self.nodeSize = (1, 4)
		self.activeNode = 0
		self.nodeCount = self.getNodeCount()
		self.deviceArrayList = []
		self.recordTime = 10
		self.recordCount = 1
		self.fps = 10.0

	def getNodeCount(self):
		return self.nodeSize[0] * self.nodeSize[1]

	def addProgressbar(self):
		self.recordingProgressBar = ProgressBar(max=1000, pos=(0, -220), width=100, height=400)
		#self.add_widget(self.recordingProgressBar)
		self.currentProgress = 0
		self.recordingProgressBar.value = self.currentProgress

	def addCameraViewButton(self):
		self.cameraViewButton = Button(text='Camera View', pos_hint={'x':.85, 'y':.25}, size_hint = (.125,.2))
		#self.cameraViewButton = Button(text='Camera View', pos=(670, Window.size[1] - 330), size_hint = (.125,.20833))
		self.cameraViewButton.bind(on_press=self.showWebcamFeed)
		self.add_widget(self.cameraViewButton)

	def addNodeIncrementButton(self):
		self.nodeIncrement = Button(text='GO', pos_hint={'x':.85, 'y':.01}, size_hint = (.125,.2))
		#self.nodeIncrement = Button(text='Settings', pos=(670, Window.size[1] - 440), size_hint = (.125,.20833))
		self.nodeIncrement.background_color = (0,255,0,0.6)
		self.nodeIncrement.bind(on_press=self.goCNC)
		self.add_widget(self.nodeIncrement)

	def addSettingsButton(self):
		self.settingsButton = Button(text='Controls', pos_hint={'x':.7, 'y':.25}, size_hint = (.125,.2))
		#self.settingsButton = Button(text='Settings', pos=(560, Window.size[1] - 330), size_hint = (.125,.20833))
		self.settingsButton.bind(on_press=self.keys)
		self.add_widget(self.settingsButton)

	def addStopButton(self):
		self.stopButton = Button(text='STOP', pos_hint={'x':.7, 'y':.01}, size_hint = (.125,.2))
		#self.stopButton = Button(text='STOP', pos=(560, Window.size[1] - 440), size_hint = (.125,.20833))
		self.stopButton.background_color = (255,0,0,0.6)
		self.stopButton.bind(on_press=self.changeActiveNode)
		self.add_widget(self.stopButton)

	def addStatusLabel(self):
		self.statusLabel = Label(text='Current status:')
		self.statusLabel.font_size = '20sp'
		#self.statusLabel.pos = (-310, -20)
		self.statusLabel.pos_hint = {'x':-.38, 'y':-.2}
		#self.statusLabel.texture_update()
		#self.statusLabel.size_hint = {'x':-.38, 'y':-.15}
		self.add_widget(self.statusLabel)

	def addTimeLeftLabel(self):
		self.timeLeftLabel = Label(text='Time left in recording:')
		self.timeLeftLabel.font_size = '20sp'
		# self.timeLeftLabel.pos = (-271, -90)
		self.timeLeftLabel.pos_hint = {'x':-.335, 'y':-.3}
		self.add_widget(self.timeLeftLabel)

	def addCameraPositionLabel(self):
		self.cameraPositionLabel = Label(text='Camera position (X,Y):')
		self.cameraPositionLabel.font_size = '20sp'
		#self.cameraPositionLabel.pos = (-267, -160)
		self.cameraPositionLabel.pos_hint = {'x':-.335, 'y':-.4}
		self.add_widget(self.cameraPositionLabel)

	def addTimeLeftValueLabel(self):
		self.timeLeftValueLabel = Label(text=str(10-int(time.time() - self.startTime)))
		self.timeLeftValueLabel.font_size = '20sp'
		self.timeLeftValueLabel.pos_hint = {'x':-.1, 'y':-.3}
		#self.timeLeftValueLabel.pos = (-120, -90)
		self.add_widget(self.timeLeftValueLabel)

	def addCurrentStatusLabel(self):
		self.currentStatusLabel = Label(text=self.currentStatus)
		self.currentStatusLabel.font_size = '20sp'
		#self.currentStatusLabel.pos = (-100, -20)
		self.currentStatusLabel.pos_hint = {'x':-.1, 'y':-.2}
		self.add_widget(self.currentStatusLabel)

	def addNodeLabels(self):
		self.activeNodeLabels = []
		for x in range (0,4):
			if len(self.nodeQueue) < 4:
				self.nodeQueue.append("")
		for x in range(0,4):
			self.nodeLabel = Label(text = self.nodeQueue[3 - x])
			self.nodeLabel.font_size = '25sp'
			self.nodeLabel.pos_hint = {'x': .375 - x * .25, 'y':.23}
			self.add_widget(self.nodeLabel)
			self.activeNodeLabels.append(self.nodeLabel)

	def recordNodes(self):
		for num, node in enumerate(self.deviceArrayList, start=1):
			# if num > self.nodeCount:
			# 	break
			if num > 3:
				break
			webcamThread = WebcamThread(num, num)
			webcamThread.start()
			#webcamThread.join()
			while webcamThread.isAlive():
				pass
			self.changeActiveNode3()
			#print("Device {}: {}".format(num, node))

	def importSettings(self, filename):
		with open(filename) as file:
			config = json.load(file)
		return config

	def setParameters(self):
		self.settingsFilename = 'settings.dat'
		self.nodeActivityFilename = 'nodestatus.dat'
		self.currentSettings = self.importSettings(self.settingsFilename)
		self.recordingTime = self.currentSettings['RecordingTime']
		self.framesPerSecond = self.currentSettings['FramesPerSecond']
		self.timeBetweenImages = self.currentSettings['TimeBetweenImages']
		self.numberOfRecordings = self.currentSettings['NumberOfRecordings']
		self.distanceVertical = self.currentSettings['DistanceVertical']
		self.distanceHorizontal = self.currentSettings['DistanceHorizontal']

	def goCNC(self, instance):
		go(self)

	def keys(self, instance):
		keyControl(self)

	#def calibrateCNC(self, instance):
	#	calThread = CNCThread(1, "calThread")
	#	calThread.start()


class StatusInterface(App):
	def build(self):
		homeScreen = Home()
		Clock.schedule_interval(homeScreen.updateTimeRemaining, 1)
		return homeScreen

class WebcamThread(threading.Thread):
   
   def __init__(self, threadID, location, func, recordingTime, numberOfRecordings, fps, imageInterval):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.location = location
      self.name = 'node ' + str(location)
      self.cameraTools = func
      self.numberOfRecordings = numberOfRecordings
      self.recordingTime = recordingTime
      self.fps = fps
      self.imageInterval = imageInterval
   
   def run(self):
      print ("Starting " + self.location)
      self.cameraTools.recordNode(self.location, self.numberOfRecordings, self.recordingTime, self.imageInterval, self.fps)
      print ("Exiting " + self.location)

#class CNCThread(threading.Thread):
#   
#	def __init__(self, threadID, func):
#		threading.Thread.__init__(self)
#		self.threadID = threadID
#		
#	
#	def run(self):
#		print ("Starting " + self.name)
      # self.cameraTools.initializeCamera(4)
      # self.cameraTools.record(10)
      # self.cameraTools.view()
      #self.cameraTools.recordNode(self.location, 1, 10)
#		cncmain3.calibrate()
#		print ("Exiting " + self.name)



if __name__ == '__main__':
	StatusInterface().run()

with Listener(
        on_press=on_press) as listener:
    listener.join()

