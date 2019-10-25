from adafruit_motorkit import MotorKit
from adafruit_motor import stepper


# kit.stepperX.onestep(direction=stepper.FORWARD/BACKWARD, style=stepper.SINGLE/DOUBLE/INTERLEAVED/MICROSTEP)

class Control:
    x_stepperWidth = 100  # todo find this
    y_stepperHeight = 100  # todo find this
    x_stepperOffset = 100  # todo find this
    y_stepperOffset = 100  # todo find this
    startingPos = [x_stepperOffset, y_stepperOffset]  
    x_currentPos = 0
    y_currentPos = 0
    currentPos = [x_currentPos, y_currentPos]
    endOfX = x_stepperWidth * 16
    endOfY = y_stepperHeight * 6
    kit = MotorKit()
    currentChipNum = 0
    currentChipXY = [0, 0]

    def __init__(self):
        pass

    # Stepper motor
    def releaseSteppers(self): #SAFE
        self.kit.stepper2.release()
        self.kit.stepper1.release()

    def calibrate(self): #SAFE
        # # this is basically home except you move until bump switch is triggered
        # todo move the stepper2 backwards until bump switch is triggered
        # todo move the stepper1 backwards until the bump switch is triggered
        self.x_currentPos = 0
        self.y_currentPos = 0
        


    def home(self): #SAFE
        for x in range(self.x_currentPos, 0, -1):
            self.kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
        for y in range(self.y_currentPos, 0, -1):
            self.kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
        self.x_currentPos = 0
        self.y_currentPos = 0


    def getBackToFirstChip(self):
        self.home()
        for x in range(self.x_stepperOffset):
            self.kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
        self.x_currentPos = self.x_stepperOffset
        for y in range(self.y_stepperOffset):
            self.kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
        self.y_currentPos = self.y_stepperOffset
        self.currentChipNum = 0
        self.currentChipXY = [0, 0]

    def moveToNextChip(self):
        for i in range(self.x_stepperWidth):  # TODO Get value to move to next chip
            self.kit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
        self.x_currentPos += self.x_stepperWidth
        self.currentChipNum += 1
        self.currentChipXY[0] += 1

    def moveUpRow(self):
        # Moves us across
        for x in range(self.x_currentPos, self.startingPos[0], -1):
            self.kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
        self.x_currentPos = self.x_stepperOffset
        # Moves us up
        for y in range(self.x_stepperWidth):
            self.kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
        self.y_currentPos += self.y_stepperHeight
        self.currentChipNum += 1
        self.currentChipXY[0] = 0
        self.currentChipXY[1] += 1