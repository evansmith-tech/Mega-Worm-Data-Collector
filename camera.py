import cv2
import time
import os

class Camera:
    vid_capture = cv2.VideoCapture(0)
    vid_cod = cv2.VideoWriter_fourcc(*'XVID')
    outputFilePath = './'
    def __init__(self, _outputFilePath):
        self.outputFilePath = os.path.dirname(_outputFilePath) # takes our string and converts it to a file path
        # If the directory already exists, we don't create it 
        # but we can still access it later on obviously
        # stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
        os.makedirs(self.outputFilePath, exist_ok=True) # Creates the nested directories needed by the user
                
                        
    def record(self, _secondsToRecord, _filename, _fps = self.get(cv2.CV_CAP_PROP_FPS), _height = self.get(cv2.CV_CAP_PROP_FRAME_HEIGHT), _width = self.get(cv2.CV_CAP_PROP_FRAME_WIDTH)):
        filePath = self.outputFilePath + "/" + _filename + ".mp4"
        output = cv2.VideoWriter(filePath, self.vid_cod, _fps, (_height , _width))

        endTime = time.time() + _secondsToRecord
        while(time.time() <= endTime):
            # Capture each frame of webcam video
            ret,frame = self.vid_capture.read()
            output.write(frame)

        # close the already opened camera
        self.vid_capture.release()
        # close the already opened file
        output.release()
        

    def disconnectCamera(self):
        # Disconects camera
        self.vid_capture.release()

    def switchCamera(self, _newValue):
        self.vid_capture = cv2.VideoCapture(_newValue)
