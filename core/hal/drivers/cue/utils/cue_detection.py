import numpy as np
import cv2
import json

def init(filename_bg = "background_no_warped.jpg"):
    with open('home/hal/drivers/cue/utils/data.json', 'r') as f:
        data = json.load(f)
    empty_bg = cv2.imread(f"core/hal/drivers/cue/utils/{filename_bg}")
    return data,empty_bg

def ImageProcessing(img,camera_data): #Process a frame : gray scale + warpPerspective
    img = img[:,:,2]
    img = cv2.warpPerspective(img, np.array(camera_data["m_camera2screen"]), (1920,1080), flags=cv2.INTER_LINEAR)
    return img

def FromTyToPoints(lefty,righty,frame):
    i=[0,lefty]
    j=[frame.shape[1]-1,righty]
    #print(i,j)

    # Calculate the coefficients. y=ax+b
    a = (j[1] - i[1]) / (j[0] - i[0])
    b = i[1] - a * i[0]

    # print('slope: ', a)
    # print('intercept: ', b)

    if(lefty<0):
        i=[int(-b/a),0]
    if(lefty>frame.shape[1]-1):
        i=[int(-b/a),frame.shape[1]-1]

    if(righty<0):
        j=[int(-b/a),0]
    if(righty>frame.shape[1]-1):
        j=[int(-b/a),frame.shape[1]-1]

    #print(i,j)
    return i,j

def CueDetection(empty_bg,frame,camera_data):
    cue = False
    lefty,righty = -1,-1
    empty_bg = ImageProcessing(empty_bg,camera_data)
    frame = ImageProcessing(frame, camera_data)

    #Images soustraction and processing
    soustraction=cv2.absdiff(empty_bg, frame)
    soustraction=cv2.GaussianBlur(soustraction,(5,5),0)
    _, soustraction = cv2.threshold(soustraction, 100, 255, cv2.THRESH_BINARY)

    #Contours detection
    contours, _ = cv2.findContours(soustraction, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        lX=[x for [[x, _]] in c]
        lY=[y for [[_, y]] in c]
        if np.corrcoef(lX, lY)[0, 1]**2 > 0.83:
            cue = True
            [vx,vy,u,v] = cv2.fitLine(c, cv2.DIST_L2, 0, 0.01, 0.01)

            # Now find two extreme points on the line to draw line
            lefty = int((-u*vy/vx) + v)
            righty = int(((frame.shape[1]-u)*vy/vx)+v)
    i,j=FromTyToPoints(lefty,righty,frame)

    return [cue, i,j]
