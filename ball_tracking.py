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
import requests

x1=200
x2=300
y1=80
y2=450

golfballradius = 21.33; # in mm

actualFPS = 0

videoStartTime = time.time()

# initialize variables to store the start and end positions of the ball
startCircle = (0, 0, 0)
endCircle = (0, 0, 0)
startPos = (0,0)
endPos = (0,0)
startTime = time.time()
pixelmmratio = 0

# initialize variable to store start candidates of balls
startCandidates = []

# Initialize Entered indicator
entered = False
started = False
left = False

#coord of polygon in frame::: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
coord=[[x1,y1],[x2,y1],[x1,y2],[x2,y2]]

speed = 0

tim1 = 0
tim2 = 0

out1 = cv2.VideoWriter('Ball-New.mp4',0x00000021, 60.0, (640, 360))

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
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "white"
# ball in the HSV color space, then initialize the
# list of tracked points
# greenLower = (200, 200,200)
# greenUpper = (255, 255, 255)
# lower_white = np.array([52,0,211])
# upper_white = np.array([105,255,255])

# for Colorpicker
# default white option
hsvVals = {'hmin': 0, 'smin': 210, 'vmin': 143, 'hmax': 50, 'smax': 255, 'vmax': 255}

if args.get("ballcolor", False):
    match args["ballcolor"]:
        case "white":
            hsvVals = {'hmin': 0, 'smin': 210, 'vmin': 143, 'hmax': 50, 'smax': 255, 'vmax': 255}
        case "yellow":
            hsvVals = {'hmin': 0, 'smin': 188, 'vmin': 0, 'hmax': 15, 'smax': 255, 'vmax': 255} #{'hmin': 2, 'smin': 207, 'vmin': 102, 'hmax': 54, 'smax': 240, 'vmax': 254}
        case "orange":
            hsvVals = {'hmin': 19, 'smin': 237, 'vmin': 168, 'hmax': 49, 'smax': 255, 'vmax': 255}# light
        case "darkorange":
            hsvVals = {'hmin': 0, 'smin': 200, 'vmin': 90, 'hmax': 60, 'smax': 255, 'vmax': 255}# dark
        case "green":
            hsvVals = {'hmin': 200, 'smin': 200, 'vmin': 200, 'hmax': 255, 'smax': 255, 'vmax': 255}# light
        case "darkgreen":
            hsvVals = {'hmin': 0, 'smin': 112, 'vmin': 150, 'hmax': 56, 'smax': 251, 'vmax': 255}# dark              
        case "red":
            hsvVals = {'hmin': 0, 'smin': 46, 'vmin': 100, 'hmax': 44, 'smax': 255, 'vmax': 255}
        case _:
            hsvVals = {'hmin': 0, 'smin': 210, 'vmin': 143, 'hmax': 50, 'smax': 255, 'vmax': 255}

    
# Create the color Finder object set to True if you need to Find the color

if args.get("img", False):
    myColorFinder = ColorFinder(True)
else:
    myColorFinder = ColorFinder(False)

#myColorFinder = ColorFinder(True)

pts = deque(maxlen=args["buffer"])
tims = deque(maxlen=args["buffer"])

webcamindex = 0

# if a webcam index is supplied, grab the reference
if args.get("camera", False):
    webcamindex = args["camera"]

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(webcamindex).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
    

def GetAngle (p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dX = x2 - x1
    dY = y2 - y1
    rads = math.atan2 (-dY, dX) #wrong for finding angle/declination?
    return math.degrees (rads)

# allow the camera or video file to warm up
time.sleep(2.0)

while True:
    
    
    # set the frameTime
    frameTime = time.time()
    actualFPS = actualFPS + 1
    videoTimeDiff = frameTime - videoStartTime
    fps = actualFPS / videoTimeDiff

    if args.get("img", False):
        frame = cv2.imread(args["img"])
    else:
        # grab the current frame
        frame = vs.read()

        # handle the frame from VideoCapture or VideoStream
        frame = frame[1] if args.get("video", False) else frame

        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            print("no frame")
            break
    
    # cropping needed for video files as they are too big
    if args.get("video", False):   
        # wait for debugging
        cv2.waitKey(10)
        # print("cropping image")
        # frame = frame[350:-100, :]
    
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

        x = 0
        y = 0
        radius = 0
        center= (0,0)
        
        for index in range(len(cnts)):
            rangefactor = 100
            cv2.drawContours(frame, cnts, index, (60, 255, 255), 1)
            ((tempcenterx, tempcentery), tempradius) = cv2.minEnclosingCircle(cnts[index])
            cv2.putText(frame,"Radius:"+str(int(tempradius)),(int(tempcenterx)+3, int(tempcentery)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
            # Eliminate countours that are outside the y dimensions of the detection zone
            if (tempcentery >= y1 and tempcentery <= y2):
                # Eliminate countours significantly different than startCircle by comparing radius in range
                if (started == True and startCircle[2]+rangefactor > tempradius and startCircle[2]-rangefactor < tempradius):
                    x = int(tempcenterx)
                    y = int(tempcentery)
                    radius = int(tempradius)
                    center= (x,y)
                    #print("Radius in Range: "+str(center)+" "+str(startCircle[2]+rangefactor)+" > "+str(radius)+" AND "+str(startCircle[2]-rangefactor)+" < "+str(radius))
                    
                else:
                    if not started:
                        x = int(tempcenterx)
                        y = int(tempcentery)
                        radius = int(tempradius)
                        center= (x,y)
                        #print("No Startpoint Set Yet: "+str(center)+" "+str(startCircle[2]+rangefactor)+" > "+str(radius)+" AND "+str(startCircle[2]-rangefactor)+" < "+str(radius))
            else:
                break
            
            
            #print(cnts)
            

            # only proceed if the radius meets a minimum size
            if radius >=5:
                # radius = 30
                # draw the circle and centroid on the frame,
                # then update the list of tracked points  
                circle = (x,y,radius)
                if circle:
                    # check if the circle is stable to detect if a new start is there
                    if not startPos or startPos[0]+10 <= center[0] or startPos[0]-10 >= center[0]:
                        startCandidates.append(center)
                        if len(startCandidates) >50 :
                            startCandidates.pop(0)
                            #filtered = startCandidates.filter(center.x == value.x and center.y == value.y)
                            arr = np.array(startCandidates)
                            # Create an empty list
                            filter_arr = []
                            # go through each element in arr
                            for element in arr:
                            # if the element is completely divisble by 2, set the value to True, otherwise False
                                if (element[0] == center[0] and center[1] == element[1]):
                                    filter_arr.append(True)
                                else:
                                    filter_arr.append(False)

                            filtered = arr[filter_arr]

                            #print(filtered)
                            if len(filtered) >= 15:
                                print("New Start Found")  
                                pts.clear()
                                tims.clear()
                                filteredcircles = []
                                filteredcircles.append(circle)
                                startCircle = circle
                                startPos = center
                                startTime = frameTime
                                #print("Start Position: "+ str(startPos[0]) +":" + str(startPos[1]))
                                # Calculate the pixel per mm ratio according to z value of circle and standard radius of 2133 mm
                                pixelmmratio = circle[2] / golfballradius
                                #print("Pixel ratio to mm: " +str(pixelmmratio))    
                                started = True            
                                entered = False
                                left = False
                                # update the points and tims queues
                                pts.appendleft(center)
                                tims.appendleft(frameTime)

                            else:

                                if (x >= coord[0][0] and entered == False and started == True):
                                    cv2.line(frame, (coord[0][0], coord[0][1]), (coord[2][0], coord[2][1]), (0, 255, 0),2)  # Changes line color to green
                                    tim1 = frameTime
                                    print("Ball Entered. Position: "+str(center))
                                    startPos = center
                                    entered = True
                                    # update the points and tims queues
                                    pts.appendleft(center)
                                    tims.appendleft(frameTime)
                                else:

                                    if ( x > coord[1][0] and entered == True and started == True):
                                        #calculate hla for circle and pts[0]
                                        previousHLA = (GetAngle((startCircle[0],startCircle[1]),pts[0])*-1)
                                        #calculate hla for circle and now
                                        currentHLA = (GetAngle((startCircle[0],startCircle[1]),center)*-1)
                                        #check if HLA is inverted
                                        similarHLA = False
                                        if left == True:
                                            if ((previousHLA <= 0 and currentHLA <=0) or (previousHLA >= 0 and currentHLA >=0)):
                                                hldDiff = (pow(currentHLA, 2) - pow(previousHLA, 2))
                                                if  hldDiff < 30:
                                                    similarHLA = True
                                            else:
                                                similarHLA = False
                                        else:
                                            similarHLA = True
                                        if ( x > pts[0][0] and (pow((y - (pts[0][1])), 2)) <= pow((y - (pts[1][1])), 2) and similarHLA == True):
                                            cv2.line(frame, (coord[1][0], coord[1][1]), (coord[3][0], coord[3][1]), (0, 255, 0),2)  # Changes line color to green
                                            tim2 = frameTime # Final time
                                            print("Ball Left. Position: "+str(center))
                                            left = True
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
                                                if not timeElapsedSeconds  == 0:
                                                    speed = ((distanceTraveledMM / 1000 / 1000) / (timeElapsedSeconds)) * 60 * 60 * 0.621371
                                                # debug out
                                                print("Time Elapsed in Sec: "+str(timeElapsedSeconds))
                                                print("Distance travelled in MM: "+str(distanceTraveledMM))
                                                print("Speed: "+str(speed)+" MPH")
                                                # update the points and tims queues
                                                pts.appendleft(center)
                                                tims.appendleft(frameTime)
                                        else:
                                            print("False Exit after the Ball")
                                        

    cv2.putText(frame,"x:"+str(startCircle[0]),(20,120),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"y:"+str(startCircle[1]),(20,140),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"radius:"+str(startCircle[2]),(20,160),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))

    # Mark Start Circle
    cv2.circle(frame, (startCircle[0],startCircle[1]), startCircle[2],(0, 0, 255), 2)
    cv2.circle(frame, (startCircle[0],startCircle[1]), 5, (0, 0, 255), -1) 

    # Mark Entered Circle
    cv2.circle(frame, (startPos), startCircle[2],(0, 0, 255), 2)
    cv2.circle(frame, (startCircle[0],startCircle[1]), 5, (0, 0, 255), -1)  

    # Mark Exit Circle
    cv2.circle(frame, (endPos), startCircle[2],(0, 0, 255), 2)
    cv2.circle(frame, (startCircle[0],startCircle[1]), 5, (0, 0, 255), -1)  



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

    timeSinceEntered = (frameTime - tim1)

    if left == True:

        # Send Shot Data
        if (tim2 and timeSinceEntered > 1 and distanceTraveledMM and timeElapsedSeconds and speed >= 0.1 and speed <= 50):
            print("----- Shot Complete --------")
            print("Time Elapsed in Sec: "+str(timeElapsedSeconds))
            print("Distance travelled in MM: "+str(distanceTraveledMM))
            print("Speed: "+str(speed)+" MPH")

            #     ballSpeed: ballData.BallSpeed,
            #     totalSpin: ballData.TotalSpin,
            totalSpin = 0
            #     hla: ballData.LaunchDirection,
            launchDirection = (GetAngle((startCircle[0],startCircle[1]),endPos)*-1)
            print("HLA: Line"+str((startCircle[0],startCircle[1]))+" Angle "+str(launchDirection))
            #Decimal(launchDirection);
            if (launchDirection > -40 and launchDirection < 40):
                    
                # Data that we will send in post request.
                data = {"ballData":{"BallSpeed":"%.2f" % speed,"TotalSpin":totalSpin,"LaunchDirection":"%.2f" % launchDirection}}

                # The POST request to our node server
                try:
                    res = requests.post('http://127.0.0.1:8888/putting', json=data)
                    res.raise_for_status()
                    # Convert response data to json
                    returned_data = res.json()

                    print(returned_data)
                    result = returned_data['result']
                    print("Response from Node.js:", result)

                except requests.exceptions.HTTPError as e:  # This is the correct syntax
                    print(e)
                except requests.exceptions.RequestException as e:  # This is the correct syntax
                    print(e)
            else:
                print("Misread on HLA - Shot not send!!!")    

            print("----- Data reset --------")
            started = False
            entered = False
            left = False
            speed = 0
            timeSinceEntered = 0
            tim1 = 0
            tim2 = 0
            distanceTraveledMM = 0
            timeElapsedSeconds = 0
            startCircle = (0, 0, 0)
            endCircle = (0, 0, 0)
            startPos = (0,0)
            endPos = (0,0)
            startTime = time.time()
            pixelmmratio = 0
            pts.clear()
            tims.clear()

            # Further clearing - startPos, endPos
    
    cv2.putText(frame,"entered:"+str(entered),(20,180),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"FPS:"+str(fps),(20,200),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    
    out1.write(frame)
    cv2.imshow("Frame", frame)
    # Comment out if HSV needs to be found
    cv2.imshow("MaskFrame", mask)
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
