import numpy as np
import cv2

webcamindex = 0 # Number of Webcamindex

vs = cv2.VideoCapture(webcamindex + cv2.CAP_DSHOW)
mjpeg = cv2.VideoWriter_fourcc('M','J','P','G')
vs.set(cv2.CAP_PROP_FOURCC, mjpeg)
vs.set(cv2.CAP_PROP_FPS, 120)
# Get video metadata
video_fps = vs.get(cv2.CAP_PROP_FPS)
print(video_fps)

while(True):

    ret, frame = vs.read()

    cv2.imshow('frame',frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vs.release()
cv2.destroyAllWindows()
