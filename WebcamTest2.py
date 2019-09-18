import cv2  

def show_webcam(mirror = False):
    scale = 30

    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        if mirror:
            img = cv2.flip(img, 1)

        # get the webcam size
        height, width, channels = img.shape

        # prepare the crop
        centerX, centerY = int(height / 2), int(width / 2)
        radiusX, radiusY = int(scale * height / 100), int(scale * width / 100)

        minX, maxX = centerX - radiusX, centerX + radiusX
        minY, maxY = centerY - radiusY, centerY + radiusY

        cropped = img[minX: maxX, minY: maxY]
        resized_cropped = cv2.resize(cropped, (width, height))

        k = cv2.waitKey(1)

        cv2.imshow('View', resized_cropped)
        if cv2.waitKey(1) == 27:
            break# esc to quit

        # add + or - 5 % to zoom

        if cv2.waitKey(1) == ord('q'):
            scale += 5# + 5

        if cv2.waitKey(1) == ord('w'):
            scale = 5# + 5

    cap.release()
    destroyEverything()
    
def destroyEverything():
    cv2.destroyAllWindows()

def main():
    show_webcam(mirror = True)

if __name__ == '__main__':
    main()