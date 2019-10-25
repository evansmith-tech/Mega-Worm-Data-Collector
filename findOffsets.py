from adafruit_motorkit import MotorKit
from adafruit_motor import stepper


kit = MotorKit()

steps = int(input("Number of Steps: "))

for i in range(steps):
    kit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)