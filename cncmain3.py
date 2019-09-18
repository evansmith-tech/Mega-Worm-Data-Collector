from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
from CameraTools import CameraTools

import curses
import time
import threading
import atexit
import RPi.GPIO as GPIO
import pickle
import os
import json

kit = MotorKit()

kit.stepper1.release()
kit.stepper2.release()

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)

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

ctools = CameraTools()


def init():
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

	nodeArray = readConfig('nodeInfo.config')['data']
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

def demomove(xloc, yloc):
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
	ctools.recordNode("A", 1, 8)

def moveRight():
	print ("RIGHT")
	for i in range (speed):
		kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	screen.clear()

def moveLeft():
	print ("LEFT")
	for i in range (speed):
		kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	screen.clear()

def moveForward():
	print ("FORDWARD")
	for i in range (speed):
		kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	screen.clear()

def moveBackwards():
	print ("BACKWARDS")
	for i in range (speed):
		kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
		time.sleep(.005)
	screen.clear()

def speedUp():
	global speed
	print ("Speed up")
	speed = (speed * 5)
	if speed == 625:
		screen.clear()
		print("Maximum speed")
		time.sleep(1)
	time.sleep(1)
	screen.clear()

def speedDown():
	global speed
	print ("Speed down")
	speed = (speed // 5)
	if speed == 1:
		screen.clear()
		print("Minimum speed")
		time.sleep(1)
	time.sleep(1)
	screen.clear()

def printLocations():
	print ("Current X = ", x_pos)
	print ("Current Y = ", y_pos)
	
	#savedlength = len(savedx)
	print("Saved locations:")
	for i in range(0,4):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	screen.clear()
	for i in range(4,8):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	screen.clear()
	for i in range(8,12):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	screen.clear()
	for i in range(12,16):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	screen.clear()
	for i in range(16,20):
		print("X: ", savedx[i], "    Y: ", savedy[i])
	time.sleep(1)
	screen.clear()

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

def go():
	global savedx, savedy, nodeArray
	rehome()
	for i in range(len(savedx)):
		if nodeArray[i] == 1:
			print("Position: ", i+1)
			demomove(savedx[i], savedy[i])
		screen.clear()
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

#main loop
def calibrate():

	global x_pos, y_pos, nodeArray

	rehome()
		
	try:
		while True:
			curses.flushinp()	#clears input buffer
			char = screen.getch() 	#get input from user
			if char == ord('q'):
				kit.stepper1.release()
				kit.stepper2.release()
				print ("Closing Calibration") 
				time.sleep(1)
				break
			elif char == curses.KEY_RIGHT:
				moveRight()
			elif char == curses.KEY_LEFT:
				moveLeft()
			elif char == curses.KEY_UP:
				moveForward()
			elif char == curses.KEY_DOWN:
				moveBackwards()

			# speeds up the motors so that
			# it is not a pain to move
			# across the machine
			elif (char == curses.KEY_PPAGE and speed <= 125):
				speedUp()

			elif (char == curses.KEY_PPAGE and speed >= 625):
				print ("Already at maximum speed")
			# slows down the motors to allow
			# for slow more precise movements
			elif (char == curses.KEY_NPAGE and speed >= 4):
				speedDown()
			elif (char == curses.KEY_NPAGE and speed <= 1):
				print ("Already at minimum speed")
				time.sleep(2)
				screen.clear()
			
			#print out locations
			elif char == ord('l'):
				printLocations()
				
				
			elif char == ord('1'):
				print ("Saved current location")
				calix[0] = x_pos
				caliy[0] = y_pos
				time.sleep(1)
				screen.clear()
			elif char == ord('2'):
				print ("Saved current location")
				calix[1] = x_pos
				caliy[1] = y_pos
				time.sleep(1)
				screen.clear()
			elif char == ord('3'):
				print ("Saved current location")
				calix[2] = x_pos
				caliy[2] = y_pos
				time.sleep(1)
				screen.clear()
			elif char == ord("p"):
				populate

				
			elif char == ord('g'):
				go()



	finally:
	#closes curses properly
		curses.nocbreak(); screen.keypad(0); curses.echo()
		curses.endwin()
		return
		
