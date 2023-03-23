# Webcam based putting simulation for GSPRO utilizing the R10 connector:

Calculation includes BallSpeed in MPH and HLA of the putt. Initial insperation on the solution comes from natter where I forked the initial OpenCV code.

These connectors integrate the putting app to use in GSPRO

- extension of original R10 connector of Travis Lang https://github.com/alleexx/gspro-garmin-connect-v2
- matth version of R10 adapter with direct bluetooth support https://github.com/mholow/gsp-r10-adapter

## Setup:

You can find a setup video here: https://youtu.be/ShtEW0fziwM

You can download the release or just install the packages and run the app via python.

Unpack the release zip and run ball_tracking.exe [-c <ballcolor OR calibrate> -w <webcamera number 0-5>]

- Position Webcam on the side and above the putting start area across from you - see video for example (flip image in "a" Advanced Settings to allow for left handed setups)
- Position the Ball (choose the right color or use calibrate as described below.) on a dark green surface - In my test the area visible to the webcam was about 1 meter high and across from me
- Adjust your webcam to the white line to reflect a straight putt and place your ball into the yellow rectangle.
- Use "a" to go to Advanced Settings - here you can adjust following settings
  - adjust camera settings by using the DirectShow camera settings window (only supported if MJPEG is enabled = 1 - dafault)
  - the start position rectangle
  - set a fixed radius if the detected radius is not consistent for you
  - flip webcam image if i.e. your a lefty
  - enable MJPEG option for changing the webcam codec to compressed MJPEG format - some webcams only support higher like 60 FPS settings on compressed video formats - auto detection of FPS settings will not work for this codec but acutal FPS should be accurate. In case the desired FPS is only available in certain resolution you can adjust/overwrite the resolution directly in the config.ini file
  - overwrite the detected FPS with a target FPS setting if not detected correctly - not all cameras support setting FPS through OpenCV
  - darken the images in case your webcam settings do not allow for this
  - beta option of ps4 enabling is done in config.ini directly
- Once identified the ball should get a red circle fully around. If it is smaller or bigger than the ball it will not reflect the right putting speed. It must match the ball dimensions as best as it can.
- If the ball is not detected try adjusting the light situation or your webcam brightness settings or try a different ball color option (hit q to exit the putting simulator and start again with another Ball Color)
- The putt needs to cross the red rectangle and needs to leave on the other side
- If a shot is detected it is send to http://localhost:8888/ where my extension of the garmin connect app (https://github.com/alleexx/gspro-garmin-connect-v2) is receiving the shot and passing it to GSPRO
  
## Some Troubleshooting steps if you can not get it to work

I guess you saw my setup video so here are some more details.

- Make sure to have a solid background. Green putting or hitting mat should be fine - The darker the better.
- Don't cast a direct shadow over the ball if possible have some light on the ball side
- Use a colored ball - orange works best for most people with color option orange2
- Use the advanced settings (hit a) to limit the detection area a bit around the ball placed
- Use the advanced settings darkness setting to limit the light reflections in the frame. Hopefully the ball will be detected in this way.
- If this does not help you can hit "d" and see the advanced debug options. It will show you the mask frame and let you see if you have any other "white" = detected spots in the area. It is also possible to directly there change the color seperation options which you could try but hopefully would not be necessary. Some people had to alter saturation and exposure in their webcam settings to get a good base image of the webcam where the colored ball really shows good.
  
Software is open source. Feel Free to buy me a coffee or a sleeve of golf balls if you like it.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U6U2I70HX)

<img src="Camera-Putting-Alignment.png">

Here is a short video demonstration of the prototype

https://youtu.be/ZgcH25WkCWQ

  
## Details on the python app

You can install the necessary packages by running pip install with the requirements file - some mentioned packages might not be necessary to run it as I did not clean it up yet

Install the app:

"pip install -r requirements.txt"

Run the app:

"python ball_tracking.py"

Default color to be found is yellow - You can adapt this by running -c as color options yellow, green, orange, red or white. White is a very general option if no color ball is availabe but might give you more false reads on other white objects. Best options for me are orange, yellow and red.

"python ball_tracking.py -c orange"

In the app you can hit "a" for advanced settings to define the ball detection area, flip and darken image or hit "d" to get a debug view of the video feed to see the color detection mask.

There are also other options to for start to pass a video file or image file

usage: ball_tracking.py [-h] [-v VIDEO] [-i IMG] [-b BUFFER] [-w CAMERA] [-c BALLCOLOR] [-d DEBUG]

options:

  -h, --help                  show this help message and exit

  -v VIDEO, --video VIDEO     path to the (optional) video file

  -i IMG, --img IMG           path to the (optional) image file

  -b BUFFER, --buffer BUFFER  max buffer size - default is 64

  -w CAMERA, --camera CAMERA  webcam index number - default is 0

  -c BALLCOLOR, --ballcolor   ball color - default is white

  -d DEBUG, --debug DEBUG     debug - color finder and wait timer




