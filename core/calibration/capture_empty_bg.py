import cv2

filename = "home/background.jpg"

#display black background
cv2.namedWindow("Billard", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Billard", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

#Config camera
CAM_NUMBER = 0
with open("home/config.json", "r") as f:
                config = json.load(f)
                if ("camera" in config and "number" in config["camera"]):
                    CAM_NUMBER = config["camera"]["number"]

cap = cv2.VideoCapture(CAM_NUMBER)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

ret,frame = cap.read()
if ret:
    cv2.imwrite(filename,frame)
    print("The background has been reset")
else:
    print("The background could not have been reset. Error in capture_empty_bg.py")

print("Note: don't forget to hide the mouse clicker icon ;)")