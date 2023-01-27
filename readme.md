# Prototype for Webcam based putting simulation for GSPRO utilizing the R10 connect package:

Calculation includes BallSpeed in MPH and HLA of the putt. 

Setup:

- Position Webcam on the side an above the putting start area across from you (currently for a right handed player) - see video for example
- Position the Ball (white is default but you can select it before starting the puttig simulator) on a dark green surface - In my test the area visible to the webcam was about 60 centimeters high and across from me
- Adjust your webcam to the white line to reflect a straight put and place your ball into the yellow rectangle.
- Once identified the ball should get a red circle fully around. If it is smaller than the ball it will not reflect the right putting speed. It must match the ball dimensions as best as it can.
- If the ball is not detected try adjusting the light situation or try a different ball color option (hit q to exit the putting simulator and start again with another Ball Color)
- The putt needs to cross the red rectangle and needs to leave on the other side
- If a shot is detected it is send to http://localhost:8888/ where my extension of the garmin connect app (https://github.com/alleexx/gspro-garmin-connect-v2) is receiving the shot and passing it to GSPRO

You can download the beta release or just install the packages and run the app via python.

Unpack the release zip and run ball_tracking.exe [-c <ballcolor OR calibrate> -w <webcamera number 0-3>]

You can install the necessary packages by running pip install with the requirements file - some mentioned packages might not be necessary to run it as I did not clean it up yet

Install the app:

"pip install -r requirements.txt"

Run the app:

"python ball_tracking.py"

Default color to be found is yellow - You can adapt this by running -c as color options yellow, green, orange, red or white. White is a very general option if no color ball is availabe but might give you more false reads on other white objects. Best options for me are orange, yellow and red.

"python ball_tracking.py -c orange"

<img src="Camera-Putting-Alignment.png">

This is early development so happy about feedback but do not base your SGT career on it

Here is a short video demonstration of the prototype

https://youtu.be/ZgcH25WkCWQ



