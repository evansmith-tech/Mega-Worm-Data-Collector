# import Control
from .camera import Camera
from datetime import datetime

# todo finish the control library, pull the final version down then import it like a file
control = None  # todo this is here to prevent errors until control is done

# control = Control()
cam = Camera()


# control.calibrate()
def main():
    running_flag = True
    while running_flag:
        while control.y_currentPos <= control.endOfY:  # should we use range tolerance? range(control.endOfY, control.endOfY + 5)
            while control.x_currentPos <= control.endOfX:
                print(f'Recording chip on Array: [{control.currentChipXY[0]}, {control.currentChipXY[1]}]')
                cam.record(5, returnFilePath(), 10)  # 5 seconds, filename, 10 fps
                control.moveToNextChip()
            print("Finished this Row")
            control.moveUpRow()

        print("Going for another pass")
        control.home()
        control.getBackToFirstChip()


main()


# todo change chipNum param to control.currentChipNum
def returnFilePath():
    now = datetime.now()
    datetime_str = now.strftime("%d/%m/%Y_%H:%M:%S")
    #todo decide on naming schema with sid
    return f'{control.currentChipNum}_{datetime_str}_'
