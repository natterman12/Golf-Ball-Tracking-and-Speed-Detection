# import the necessary packages
from collections import deque
import numpy as np
import argparse
import cv2
import imutils
import time
import sys
import cvzone
from ColorModuleExtended import ColorFinder
import math
from decimal import *
import requests

# Startpoint Zone

sx1=10
sx2=180

y1=180
y2=450

#coord of polygon in frame::: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
startcoord=[[sx1,y1],[sx2,y1],[sx1,y2],[sx2,y2]]

# Detection Gateway
x1=sx2+10
x2=200

#coord of polygon in frame::: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
coord=[[x1,y1],[x2,y1],[x1,y2],[x2,y2]]

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
startminimum = 10

# Initialize Entered indicator
entered = False
started = False
left = False

lastShotStart = (0,0)
lastShotEnd = (0,0)
lastShotSpeed = 0
lastShotHLA = 0 

speed = 0

tim1 = 0
tim2 = 0


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
args = vars(ap.parse_args())

# define the lower and upper boundaries of the different ball color options (-c)
# ball in the HSV color space, then initialize the

#red                   
red = {'hmin': 1, 'smin': 208, 'vmin': 0, 'hmax': 50, 'smax': 255, 'vmax': 249} # light
red2 = {'hmin': 1, 'smin': 240, 'vmin': 61, 'hmax': 50, 'smax': 255, 'vmax': 249} # dark

#white
white = {'hmin': 168, 'smin': 218, 'vmin': 118, 'hmax': 179, 'smax': 247, 'vmax': 216} # very light
white2 = {'hmin': 159, 'smin': 217, 'vmin': 152, 'hmax': 179, 'smax': 255, 'vmax': 255} # light

#yellow

yellow = {'hmin': 0, 'smin': 210, 'vmin': 0, 'hmax': 15, 'smax': 255, 'vmax': 255} # light
yellow2 = {'hmin': 0, 'smin': 150, 'vmin': 100, 'hmax': 46, 'smax': 255, 'vmax': 206} # dark

#green
green = {'hmin': 0, 'smin': 169, 'vmin': 161, 'hmax': 177, 'smax': 204, 'vmax': 255} # light
green2 = {'hmin': 0, 'smin': 109, 'vmin': 74, 'hmax': 81, 'smax': 193, 'vmax': 117} # dark

#orange
orange = {'hmin': 0, 'smin': 219, 'vmin': 147, 'hmax': 19, 'smax': 255, 'vmax': 255}# light
orange2 = {'hmin': 3, 'smin': 181, 'vmin': 134, 'hmax': 40, 'smax': 255, 'vmax': 255}# dark
orange3 = {'hmin': 0, 'smin': 73, 'vmin': 150, 'hmax': 40, 'smax': 255, 'vmax': 255}# test

calibrate = {}

# for Colorpicker
# default yellow option
hsvVals = yellow

if args.get("ballcolor", False):
    match args["ballcolor"]:
        case "white":
            hsvVals = white
        case "white2":
            hsvVals = white2
        case "yellow":
            hsvVals = yellow 
        case "yellow2":
            hsvVals = yellow2 
        case "orange":
            hsvVals = orange
        case "orange2":
            hsvVals = orange2
        case "orange3":
            hsvVals = orange3
        case "green":
            hsvVals = green 
        case "green2":
            hsvVals = green2               
        case "red":
            hsvVals = red             
        case "red2":
            hsvVals = red2   
        case _:
            hsvVals = yellow

calibrationcolor = [("white",white),("white2",white2),("yellow",yellow),("yellow2",yellow2),("orange",orange),("orange2",orange2),("orange3",orange3),("green",green),("green2",green2),("red",red),("red2",red2)]
    
# Create the color Finder object set to True if you need to Find the color

if args.get("debug", False):
    myColorFinder = ColorFinder(True)
    myColorFinder.setTrackbarValues(hsvVals)
else:
    myColorFinder = ColorFinder(False)

pts = deque(maxlen=args["buffer"])
tims = deque(maxlen=args["buffer"])

webcamindex = 0

# if a webcam index is supplied, grab the reference
if args.get("camera", False):
    webcamindex = args["camera"]

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = cv2.VideoCapture(webcamindex) # VideoStream(webcamindex).start()
    # otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# Get video metadata
video_fps = vs.get(cv2.CAP_PROP_FPS),
height = vs.get(cv2.CAP_PROP_FRAME_HEIGHT)
width = vs.get(cv2.CAP_PROP_FRAME_WIDTH)

# we are using x264 codec for mp4
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out1 = cv2.VideoWriter('Ball-New.mp4', apiPreference=0, fourcc=fourcc,fps=video_fps[0], frameSize=(int(width), int(height)))
out2 = cv2.VideoWriter('Calibration.mp4', apiPreference=0, fourcc=fourcc,fps=video_fps[0], frameSize=(int(width), int(height)))

    

def GetAngle (p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dX = x2 - x1
    dY = y2 - y1
    rads = math.atan2 (-dY, dX) #wrong for finding angle/declination?
    return math.degrees (rads)

# allow the camera or video file to warm up
time.sleep(2.0)

colorcount = 0
calibrationtime = time.time()
calObjectCount = 0
calColorObjectCount = []
calibrationTimeFrame = 30
record = True

while True:
    
    # set the frameTime
    frameTime = time.time()
    actualFPS = actualFPS + 1
    videoTimeDiff = frameTime - videoStartTime
    fps = actualFPS / videoTimeDiff

    if args.get("img", False):
        frame = cv2.imread(args["img"])
    else:
        # check for calibration
        ret, frame = vs.read()
        
        if args["ballcolor"] == "calibrate":
            if record == False:
                if args.get("debug", False):
                    cv2.waitKey(int(args["debug"]))
                if frame is None:
                    calColorObjectCount.append((calibrationcolor[colorcount][0],calObjectCount))
                    colorcount += 1
                    calObjectCount = 0
                    if colorcount == len(calibrationcolor):
                        vs.release()
                        vs = cv2.VideoCapture(webcamindex)
                        ret, frame = vs.read()
                        print("Calibration Finished:"+str(calColorObjectCount))
                        cv2.putText(frame,"Calibration Finished:",(150,100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
                        i = 20
                        texty = 100
                        for calObject in calColorObjectCount:
                            texty = texty+i
                            cv2.putText(frame,str(calObject),(150,texty),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
                        texty = texty+i
                        cv2.putText(frame,"Hit any key and choose color with the highest count.",(150,texty),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
                        cv2.imshow("Putting View: Press Q to exit / changing Ball Color", frame)
                        cv2.waitKey(0)
                        # Show Results back to Connect App and set directly highest count - maybe also check for false Exit lowest value if 2 colors have equal hits
                        break
                    else:
                        vs.release()                        
                        # grab the calibration video
                        vs = cv2.VideoCapture('Calibration.mp4')
                        # grab the current frame
                        ret, frame = vs.read()
                else:
                    hsvVals = calibrationcolor[colorcount][1]
                    if args.get("debug", False):
                        myColorFinder.setTrackbarValues(hsvVals)
                    cv2.putText(frame,"Calibration Mode:"+str(calibrationcolor[colorcount][0]),(200,100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
            else:
                if (frameTime - calibrationtime) > calibrationTimeFrame:
                    record =  False
                    out2.release()
                    vs.release()
                    # grab the calibration video
                    vs = cv2.VideoCapture('Calibration.mp4')
                    # grab the current frame
                    ret, frame = vs.read()
                cv2.putText(frame,"Calibration Mode:",(200,100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255)) 

        # handle the frame from VideoCapture or VideoStream
        # frame = frame[1] if args.get("video", False) else frame

        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            print("no frame")
            break

    origframe = frame
    
    # cropping needed for video files as they are too big
    if args.get("debug", False):   
        # wait for debugging
        cv2.waitKey(int(args["debug"]))
    
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
    #mask = cv2.erode(mask, None, iterations=1)
    #mask = cv2.dilate(mask, None, iterations=5)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # testing with cirlces
    # grayframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # circles = cv2.HoughCircles(blurred,cv2.HOUGH_GRADIENT,1,10) 
    # # loop over the (x, y) coordinates and radius of the circles
    # if (circles and len(circles) >= 1):
    #     for (x, y, r) in circles:
    #         cv2.circle(frame, (x, y), r, (0, 255, 0), 4)
    #         cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)


    cnts = imutils.grab_contours(cnts)
    center = None
    
    # Startpoint Zone

    cv2.line(frame, (startcoord[0][0], startcoord[0][1]), (startcoord[1][0], startcoord[1][1]), (0, 210, 255), 2)  # First horizontal line
    cv2.line(frame, (startcoord[0][0], startcoord[0][1]), (startcoord[2][0], startcoord[2][1]), (0, 210, 255), 2)  # Vertical left line
    cv2.line(frame, (startcoord[2][0], startcoord[2][1]), (startcoord[3][0], startcoord[3][1]), (0, 210, 255), 2)  # Second horizontal line
    cv2.line(frame, (startcoord[1][0], startcoord[1][1]), (startcoord[3][0], startcoord[3][1]), (0, 210, 255), 2)  # Vertical right line

    # Detection Gateway

    cv2.line(frame, (coord[0][0], coord[0][1]), (coord[1][0], coord[1][1]), (0, 0, 255), 2)  # First horizontal line
    cv2.line(frame, (coord[0][0], coord[0][1]), (coord[2][0], coord[2][1]), (0, 0, 255), 2)  # Vertical left line
    cv2.line(frame, (coord[2][0], coord[2][1]), (coord[3][0], coord[3][1]), (0, 0, 255), 2)  # Second horizontal line
    cv2.line(frame, (coord[1][0], coord[1][1]), (coord[3][0], coord[3][1]), (0, 0, 255), 2)  # Vertical right line

    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    # only proceed if at least one contour was found
    if len(cnts) > 0:

        x = 0
        y = 0
        radius = 0
        center= (0,0)
        
        for index in range(len(cnts)):
            # Eliminate countours that are outside the y dimensions of the detection zone
            ((tempcenterx, tempcentery), tempradius) = cv2.minEnclosingCircle(cnts[index])
            if (tempcentery >= y1 and tempcentery <= y2):
                rangefactor = 150
                cv2.drawContours(frame, cnts, index, (60, 255, 255), 1)
                cv2.putText(frame,"Radius:"+str(int(tempradius)),(int(tempcenterx)+3, int(tempcentery)),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
                # Eliminate countours significantly different than startCircle by comparing radius in range
                if (started == True and startCircle[2]+rangefactor > tempradius and startCircle[2]-10 < tempradius):
                    x = int(tempcenterx)
                    y = int(tempcentery)
                    radius = int(tempradius)
                    center= (x,y)
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
                    if not started or startPos[0]+10 <= center[0] or startPos[0]-10 >= center[0]:
                        if (center[0] >= sx1 and center[0] <= sx2):
                            startCandidates.append(center)
                            if len(startCandidates) > startminimum :
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
                                if len(filtered) >= (startminimum/2):
                                    print("New Start Found")
                                    lastShotSpeed = 0
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
                                    if ( x > pts[0][0]and similarHLA == True): # and (pow((y - (pts[0][1])), 2)) <= pow((y - (pts[1][1])), 2) 
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
                                    
    cv2.putText(frame,"Start Ball",(20,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"x:"+str(startCircle[0]),(20,40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"y:"+str(startCircle[1]),(20,60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    cv2.putText(frame,"radius:"+str(startCircle[2]),(20,80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))

    # Mark Start Circle
    if started:
        cv2.circle(frame, (startCircle[0],startCircle[1]), startCircle[2],(0, 0, 255), 2)
        cv2.circle(frame, (startCircle[0],startCircle[1]), 5, (0, 0, 255), -1) 

    # Mark Entered Circle
    if entered:
        cv2.circle(frame, (startPos), startCircle[2],(0, 0, 255), 2)
        cv2.circle(frame, (startCircle[0],startCircle[1]), 5, (0, 0, 255), -1)  

    # Mark Exit Circle
    if left:
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
        #cv2.line(frame, pts[i - 1], pts[i], (0, 0, 150), thickness)
        # print("Point:"+str(pts[i])+"; Timestamp:"+str(tims[i]))

    timeSinceEntered = (frameTime - tim1)

    if left == True:

        # Send Shot Data
        if (tim2 and timeSinceEntered > 0.5 and distanceTraveledMM and timeElapsedSeconds and speed >= 0.3 and speed <= 30):
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

                lastShotStart = (startCircle[0],startCircle[1])
                lastShotEnd = endPos
                lastShotSpeed = speed
                lastShotHLA = launchDirection
                    
                # Data that we will send in post request.
                data = {"ballData":{"BallSpeed":"%.2f" % speed,"TotalSpin":totalSpin,"LaunchDirection":"%.2f" % launchDirection}}

                # The POST request to our node server
                if args["ballcolor"] == "calibrate":
                    print("calibration mode - shot data not send")
                else:
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
            if len(pts) > calObjectCount:
                calObjectCount = len(pts)
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
    else:
        # Send Shot Data
        if (tim1 and timeSinceEntered > 0.5):
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
            
    #cv2.putText(frame,"entered:"+str(entered),(20,180),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    #cv2.putText(frame,"FPS:"+str(fps),(20,200),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))

    if not lastShotSpeed == 0:
        cv2.line(frame,(lastShotStart),(lastShotEnd),(0, 255, 255),4,cv2.LINE_AA)      
        cv2.putText(frame,"Last Shot",(300,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
        cv2.putText(frame,"Ball Speed: "+str(lastShotSpeed)+" MPH",(300,40),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
        cv2.putText(frame,"HLA: "+str(lastShotHLA)+" Degrees",(300,60),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0, 0, 255))
    
    if started:
        cv2.line(frame,(sx2-sx1,startCircle[1]),(sx2-sx1+400,startCircle[1]),(255, 255, 255),4,cv2.LINE_AA)
    else:
        cv2.line(frame,(sx2-sx1,int(y1+((y2-y1)/2))),(sx2-sx1+400,int(y1+((y2-y1)/2))),(255, 255, 255),4,cv2.LINE_AA) 
    
    if args.get("video", False):
        out1.write(frame)

    if out2:
        out2.write(origframe)
    cv2.imshow("Putting View: Press Q to exit / changing Ball Color", frame)
    
    if args.get("debug", False):
        cv2.imshow("MaskFrame", mask)
        cv2.imshow("Original", origframe)
    
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break


# close all windows
if out1:
    out1.release()

vs.release()
cv2.destroyAllWindows()
