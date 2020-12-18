from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

# This file basically is its own standalone dealeo
# You kind of just guestimate a number whenever your camera is at (0,0). 
# This then allows you to find the distance on the x and y axis to the middle of the 1st cell.
# Hardcode it into your main.py file or stepperSwitchControls
# Profit

kit = MotorKit()

steps = int(input("Number of Steps: "))

for i in range(steps):
    kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)