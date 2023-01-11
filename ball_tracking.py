# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
import sys
import cvzone
from cvzone.ColorModule import ColorFinder
import math
from decimal import *

x1=200
x2=400
y1=10
y2=300

golfballradius = 21.33; # in mm


# initialize variables to store the start and end positions of the ball
startCircle = (0, 0, 0)
endCircle = (0, 0, 0)
startPos = (0,0)
endPos = (0,0)
startTime = time.time()
endTime = time.time()
pixelmmratio = 0

# initialize variable to store start candidates of balls
startCandidates = []

# Initialize Entered indicator
entered = False

#coord of polygon in frame::: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
coord=[[x1,y1],[x2,y1],[x1,y2],[x2,y2]]

speed = 0

dtFIL = 0

tim1 = 0
tim2 = 0

out1 = cv2.VideoWriter('Ball-New.mp4',0x00000021, 60.0, (640, 360))

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
                help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "white"
# ball in the HSV color space, then initialize the
# list of tracked points
# greenLower = (200, 200,200)
# greenUpper = (255, 255, 255)
# lower_white = np.array([52,0,211])
# upper_white = np.array([105,255,255])

# Create the color Finder object set to True if you need to Find the color
myColorFinder = ColorFinder(False)
#hsvVals = {'hmin': 0, 'smin': 185, 'vmin': 0, 'hmax': 40, 'smax': 255, 'vmax': 255}
#hsvVals = {'hmin': 52, 'smin': 0, 'vmin': 211, 'hmax': 105, 'smax': 255, 'vmax': 255}
hsvVals = {'hmin': 164, 'smin': 0, 'vmin': 0, 'hmax': 179, 'smax': 255, 'vmax': 255}

pts = deque(maxlen=args["buffer"])
tims = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
time.sleep(2.0)

while True:
    # wait for debugging
    cv2.waitKey(10)

    # grab the current frame
    frame = vs.read()

    # set the frameTime
    frameTime = time.time()

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        print("no frame")
        break
    
    # cropping needed for video files as they are too big
    if args.get("video", False):
        print("cropping image")
        frame = frame[350:-100, :]
    
    # resize the frame, blur it, and convert it to the HSV
    # color space
    frame = imutils.resize(frame, width=640, height=360)  
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # construct a mask for the color "green", then perform
    # a series of dilations and erosions to remove any small
    # blobs left in the mask
    
    # Find the Color Ball
    imgColor, mask = myColorFinder.update(hsv, hsvVals)

    # Mask now comes from ColorFinder
    #mask = cv2.inRange(hsv, lower_white, upper_white)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    
    cv2.putText(frame,"x1:"+str(x1),(20,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"y1:"+str(y1),(20,40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"x2:"+str(x2),(20,60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"y2:"+str(y2),(20,80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))

    cv2.line(frame, (coord[0][0], coord[0][1]), (coord[1][0], coord[1][1]), (0, 0, 255), 2)  # First horizontal line
    cv2.line(frame, (coord[0][0], coord[0][1]), (coord[2][0], coord[2][1]), (0, 0, 255), 2)  # Vertical left line
    cv2.line(frame, (coord[2][0], coord[2][1]), (coord[3][0], coord[3][1]), (0, 0, 255), 2)  # Second horizontal line
    cv2.line(frame, (coord[1][0], coord[1][1]), (coord[3][0], coord[3][1]), (0, 0, 255), 2)  # Vertical right line

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        
        for index in range(len(cnts)):
            cv2.drawContours(frame, cnts, index, (60, 255, 255), 1)

        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 10:
            # radius = 30
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

        
            temp = (x,y,radius)
            tempx = int(temp[0])
            tempy = int(temp[1])
            tempz = int(temp[2])
                            
            cv2.putText(frame,"x:"+str(tempx),(20,120),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
            cv2.putText(frame,"y:"+str(tempy),(20,140),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
            cv2.putText(frame,"radius:"+str(tempz),(20,160),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
            circle = (tempx,tempy,tempz)
            if tempz >=1 and tempz <= 50:
                # check if the circle is stable to detect if a new start is there
                newCenter = (tempx,tempy)
                if not startPos or startPos[0]+10 <= newCenter[0] or startPos[0]-10 >= newCenter[0]:
                    startCandidates.append(newCenter)
                    if len(startCandidates) >10 :
                        startCandidates.pop(0)
                        #filtered = startCandidates.filter(newCenter.x == value.x and newCenter.y == value.y)
                        arr = np.array(startCandidates)
                        # Create an empty list
                        filter_arr = []
                        # go through each element in arr
                        for element in arr:
                        # if the element is completely divisble by 2, set the value to True, otherwise False
                            if (element[0] == newCenter[0] and newCenter[1] == element[1]):
                                filter_arr.append(True)
                            else:
                                filter_arr.append(False)

                        filtered = arr[filter_arr]

                        #print(filtered)
                        if len(filtered) >= 5:
                            print("New Start Found")
                            filteredcircles = []
                            filteredcircles.append(circle)
                            startCircle = circle
                            startPos = newCenter
                            startTime = time.time()
                            print("Start Position: "+ str(startPos[0]) +":" + str(startPos[1]))
                            # Calculate the pixel per mm ratio according to z value of circle and standard radius of 2133 mm
                            pixelmmratio = circle[2] / golfballradius
                            print("Pixel ratio to mm: " +str(pixelmmratio))                
                            entered = False
                            # update the points and tims queues
                            pts.clear
                            tims.clear
                            pts.appendleft(center)
                            tims.appendleft(frameTime)

                        else:

                            if (x >= coord[1][0] and entered == False):
                                cv2.line(frame, (coord[1][0], coord[1][1]), (coord[3][0], coord[3][1]), (0, 255, 0),2)  # Changes line color to green
                                tim1 = frameTime
                                print("Ball Entered. Position: "+str(center)) 
                                startPos = center
                                entered = True
                                # update the points and tims queues
                                pts.appendleft(center)
                                tims.appendleft(frameTime)
                            else:

                                if ( x >= coord[0][0] and entered == True):
                                    cv2.line(frame, (coord[0][0], coord[0][1]), (coord[2][0], coord[2][1]), (0, 255, 0),2)  # Changes line color to green
                                    tim2 = frameTime # Final time
                                    print("Ball Left. Position: "+str(center)) 
                                    endPos = center
                                    # calculate the distance traveled by the ball in pixel
                                    a = endPos[0] - startPos[0]
                                    b = endPos[1] - startPos[1]
                                    distanceTraveled = math.sqrt( a*a + b*b )
                                    if not pixelmmratio is None:
                                        # convert the distance traveled to mm using the pixel ratio
                                        distanceTraveledMM = distanceTraveled / pixelmmratio
                                        # take the time diff from ball entered to this frame
                                        timeElapsedSeconds = (tim2 - tim1)
                                        # calculate the speed in MPH
                                        speed = ((distanceTraveledMM / 1000 / 1000) / (timeElapsedSeconds)) * 60 * 60 * 0.621371
                                        # debug out
                                        print("Time Elapsed in Sec: "+str(timeElapsedSeconds))
                                        print("Distance travelled in MM: "+str(distanceTraveledMM))
                                        print("Speed: "+str(speed)+" MPH")
                                        # update the points and tims queues
                                        pts.appendleft(center)
                                        tims.appendleft(frameTime)
                                    
                                    

    # loop over the set of tracked points
    for i in range(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 1.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 150), thickness)
        # print("Point:"+str(pts[i])+"; Timestamp:"+str(tims[i]))

    timeSinceEntered = (frameTime - tim2)

    if (tim2 and timeSinceEntered > 1 and distanceTraveledMM and timeElapsedSeconds):
        print("----- Shot Complete --------")
        print("Time Elapsed in Sec: "+str(timeElapsedSeconds))
        print("Distance travelled in MM: "+str(distanceTraveledMM))
        print("Speed: "+str(speed)+" MPH")
        print("----- Data reset --------")
        entered = False
        speed = 0
        timeSinceEntered = 0
        tim1 = 0
        tim2 = 0
        distanceTraveledMM = 0
        timeElapsedSeconds = 0
        pixelmmratio = 0
        pts.clear
        tims.clear

        # Further clearing - startPos, endPos
    
    cv2.putText(frame,"entered:"+str(entered),(20,180),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    
    out1.write(frame)
    cv2.imshow("Frame", frame)
    # Comment out if HSV needs to be found
    # cv2.imshow("Frame", mask)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()

# otherwise, release the camera
else:
	vs.release()

# close all windows
out1.release()
cv2.destroyAllWindows()
