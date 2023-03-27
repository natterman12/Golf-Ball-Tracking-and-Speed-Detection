# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import imutils

def decode(myframe):
    left = np.zeros((400,632,3), np.uint8)
    right = np.zeros((400,632,3), np.uint8)
    
    for i in range(400):
        left[i] = myframe[i, 32: 640 + 24] 
        right[i] = myframe[i, 640 + 24: 640 + 24 + 632] 
    
    return (left, right)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-i", "--img",
                help="path to the (optional) image file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size - default is 64")
ap.add_argument("-w", "--camera", type=int, default=0,
                help="webcam index number - default is 0")
ap.add_argument("-c", "--ballcolor",
                help="ball color - default is white")
ap.add_argument("-d", "--debug",
                help="debug - color finder and wait timer")
ap.add_argument("-r", "--resize", type=int, default=640,
                help="window resize in width pixel - default is 640px")
args = vars(ap.parse_args())


vs = cv2.VideoCapture(args["video"])
videofile = True

# Get video metadata

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_fps = vs.get(cv2.CAP_PROP_FPS)
height = 400 #vs.get(cv2.CAP_PROP_FRAME_HEIGHT)
width = 632 #vs.get(cv2.CAP_PROP_FRAME_WIDTH)

resizevideo = cv2.VideoWriter("resized-"+args["video"], apiPreference=0, fourcc=fourcc,fps=120, frameSize=(int(width), int(height)))

while True:
    ret, origframe = vs.read()
    if ret == True:
        leftframe, rightframe = decode(origframe)
        origframe = leftframe
        resizevideo.write(origframe)
    if origframe is None:
        resizevideo.release()
        break

# close all windows
vs.release()
cv2.destroyAllWindows()