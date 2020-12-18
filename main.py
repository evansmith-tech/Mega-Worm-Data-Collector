from .stepperSwitchControls import Control
from .camera import Camera
from datetime import datetime

# This is our glue
control = Control()
cam = Camera()
control.calibrate()

def main():
    running_flag = True 
    while running_flag:
        # TODO should we use range tolerance? something like range(control.endOfY, control.endOfY + 5), where it just has to be in that range and then we can reset?
        while control.y_currentPos <= control.endOfY:       # Move along Y axis
            while control.x_currentPos <= control.endOfX:   # Move along X axis
                print(f'Recording chip on Array: [{control.currentChipXY[0]}, {control.currentChipXY[1]}]')

                # Record current chip
                cam.record(5, generateFilePath(), 10)  # 5 seconds, filename, 10 fps

                # Move to next chip after we are done recording
                control.moveToNextChip()

            print("Finished this Row")

            #Having completed this row along the X axis, we need to move the camera up on the Y axis
            control.moveUpRow()

        print("Going for another pass")
        control.home() # go home
        control.getBackToFirstChip() # adjust in accordance with the offsets


main()

# This generates a filename for each recording using a timestamp and the current chip number
def generateFilePath():
    now = datetime.now()
    datetime_str = now.strftime("%d/%m/%Y_%H:%M:%S")
    #todo decide on naming schema with sid
    return f'{control.currentChipNum}_{datetime_str}_'



    
