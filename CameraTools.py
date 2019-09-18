import cv2
import os
import time
import datetime
import numpy as np

class CameraTools:

	def __init__(self):
		self.displayCameraView = True
		self.complete = False
		#self.createFolder('Node 1')
		self.timeRemaining = 0

	def initializeCamera(self, num, fps):
		self.cap = cv2.VideoCapture(0)
		self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
		self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
		self.out = cv2.VideoWriter(self.directoryPath + '/output ' + str(num) + '.avi', self.fourcc, fps, (1280,720))

	def record(self, duration, imageInterval):
		startTime = time.time()
		pDelta = 0
		img_counter = 0

		while(int(time.time() - startTime) < duration):
			self.recordingProgress = (int(time.time() - startTime) / duration) * 100
			self.timeRemaining = int(startTime - time.time())
			ret, frame = self.cap.read()

			delta = int(time.time() - startTime)

			if delta > pDelta:
				print(delta)

				if delta % imageInterval == 0:
					img_name = "opencv_frame_{}.png".format(img_counter)
					cv2.imwrite(self.directoryPath + img_name, frame)
					print("{} written!".format(img_name))
					img_counter += 1

			if ret == True:
				self.out.write(frame)

				if self.displayCameraView:
					cv2.imshow('framewow',frame)

				if cv2.waitKey(1) & 0xFF == ord('q'):
					self.endRecording()
					break
			else:
				break

			pDelta = delta

	def view(self):
		self.cap = cv2.VideoCapture(0)
		# self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		# self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
		while True:
			ret, frame = self.cap.read()
			if ret == True:
				cv2.imshow('framewow',frame)
				if cv2.waitKey(1) & 0xFF == ord('q'):
					self.endRecording()
					break

	def endRecording(self):
		self.cap.release()
		self.out.release()
		cv2.destroyAllWindows()
		self.complete = True

	def recordNode(self, location, count, duration, imageInterval, fps):
		for i in range(count):
			self.createFolder(location)
			self.nodeProgress = (i + 1) / count
			self.initializeCamera(i + 1, fps)
			self.record(duration, imageInterval)
			self.endRecording()
		pass

	def createFolder(self, location):
		self.directoryPath = './Recordings/' + str(location) + '/' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '/')
		try:
			if not os.path.exists(self.directoryPath):
				os.makedirs(self.directoryPath)
		except OSError:
			print ('Error: Creating directory. ' +  self.directoryPath)

# test = CameraTools()
# test.initializeCamera(1)
# test.record(10)
#test.view()

#wtfTest()