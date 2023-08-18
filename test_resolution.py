import pandas as pd
import cv2

url = "https://en.wikipedia.org/wiki/List_of_common_resolutions"
print("Reading URL")
table = pd.read_html(url)[0]
print("Reading from the local table")
table.columns = table.columns.droplevel()
webcamindex = 3 # Number of Webcamindex

cap = cv2.VideoCapture(webcamindex + cv2.CAP_DSHOW)
mjpeg = cv2.VideoWriter_fourcc('M','J','P','G')
cap.set(cv2.CAP_PROP_FOURCC, mjpeg)

resolutions = {}
for index, row in table[["W", "H"]].iterrows():
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, row["W"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, row["H"])
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    resolutions[str(width)+"x"+str(height)+"@"+str(fps)] = "OK"
print(resolutions)