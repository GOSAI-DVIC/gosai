import numpy as np
import cv2
import json

def init(filename_bg = "background_no_warped.jpg"):
    with open('platform/calibration/calibration_data.json', 'r') as f:
        data = json.load(f)
    empty_bg = cv2.imread(f"core/hal/drivers/ball/utils/{filename_bg}")
    return data,empty_bg

def ImageProcessing(img,camera_data): #Process a frame : gray scale + warpPerspective
    img = img[:,:,2]
    img = cv2.warpPerspective(img, np.array(camera_data["poolFocus_matrix"]), (1920,1080), flags=cv2.INTER_LINEAR)
    return img

def BallDetection(empty_bg,frame,camera_data):
    empty_bg = ImageProcessing(empty_bg,camera_data)
    frame = ImageProcessing(frame,camera_data)

    #Images soustraction and processing
    soustraction=cv2.absdiff(empty_bg, frame)
    soustraction=cv2.GaussianBlur(soustraction,(5,5),0)
    _, soustraction = cv2.threshold(soustraction, 100, 255, cv2.THRESH_BINARY)

    #Contours detection
    contours, _ = cv2.findContours(soustraction, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    l=[]

    for c in contours:
        M = cv2.moments(c)
        # Surface trop petite ?
        if M["m00"]<np.pi*15**2:
            continue
        lX=[x for [[x, _]] in c]
        lY=[y for [[_, y]] in c]
        
        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])
        ecartype = np.std([((x-ix)**2 + (y-iy)**2)**0.5 for ix, iy in zip(lX, lY)])
        # ça ressemble à un cercle ?
        if ecartype < 10:
            
            matrix = np.array(camera_data["projection_matrix"])
            point = np.array([[x],[y],[1]])
            outpoint = matrix.dot(point)
            # print(outpoint)
            # print(" ")
            # p = (x,y)
            # p_array = np.array([[p[0], p[1]]], dtype=np.float32)
            # transformed_points = cv2.warpPerspective(p_array, np.array(camera_data["m_camera2screen"]), (1920,1080), flags=cv2.INTER_LINEAR)
            # print(IsMatrixFullOfZero(transformed_points))
            l+=[(int(outpoint[0][0]),int(outpoint[1][0]))]
    return l

def IsMatrixFullOfZero(matrix):
    rep = False
    for i in range(1920):
        for j in range(1080):
            if(matrix[i][j] != 0):
                rep = True
                print(i,j)

    return rep