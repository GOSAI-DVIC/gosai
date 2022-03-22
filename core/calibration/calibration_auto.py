import numpy as np
import cv2
from cv2 import aruco
from itertools import permutations  
import json

projected_coords = [[550,550],[450,750],[1250,600],[1230,850]]
#projected_coords = [[400,300],[400,780],[1520,300],[1520,780]] #Original test coords
screen_coords=[[0,0], [0,1080],[1920,0],[1920,1080]]

############### Getting ancient calibration data ###############

try:
    with open('core/calibration/calibration_data.json', 'r') as f:
        data = json.load(f)

    for k,v in data.items():
        globals()[k]=np.array(v)
    
except:
    pool_coords = screen_coords
    detected_coords = projected_coords
    

############### Window Configuration ###############
cv2.namedWindow("Pool", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Pool", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


############### Camera Configuration ###############

def get_frame():

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    ok, frame = cap.read()

    cap.release()
    
    if not ok:
        cv2.destroyAllWindows()
        print("No camera detected")
        input()
        exit()
    
    return frame

############### place circle with mouseCallBack event ###############

def draw_circle(event,x,y,flags,param):
    
    global l_circle, background
    
    if event in [cv2.EVENT_RBUTTONDOWN, cv2.EVENT_LBUTTONDOWN]:
        
        if len(l_circle)>=4:
            l_circle[min(enumerate([(xC-x)**2+(yC-y)**2 for xC,yC in l_circle]), key=lambda x: x[1])[0]]=[x,y]
        else:
            l_circle+=[[x,y]]
        
        frame=background.copy()
        
        for i,p1 in enumerate(l_circle):
            p1=tuple(p1)
            for p2 in l_circle[i+1:]:
                p2=tuple(p2)
                cv2.line(frame,p1,p2,(255,0,0),3)
            cv2.circle(frame,p1,20,(0,0,255),-1)
        
        cv2.imshow('Pool',frame)


############### Pool Calibration ###############

background=get_frame()

cv2.putText(background,
            "Click on pool 4 corners",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)

l_circle=pool_coords
cv2.imshow('Pool', background)

cv2.setMouseCallback('Pool', draw_circle)

frame=background.copy()
for i,p1 in enumerate(l_circle):
    p1=tuple(p1)
    for p2 in l_circle[i+1:]:
        p2=tuple(p2)
        cv2.line(frame,p1,p2,(255,0,0),3)
    cv2.circle(frame,p1,20,(0,0,255),-1)

cv2.imshow('Pool',frame)

cv2.waitKey(0)
while len(l_circle)<4:
    cv2.waitKey(0)
    
cv2.setMouseCallback('Pool', lambda *args: None)
    
pool_coords=l_circle.copy()

frame_camera=background.copy()

############### Calibration Projecteur ###############

def drawArucoFrame():
    #place aruco patters on images at projected_coords coordinates
    arucoFrame=np.full((1080,1920,3), 255,np.uint8)

    aruco0 = cv2.imread("home/calibration/aruco0.png")
    aruco1 = cv2.imread("home/calibration/aruco1.png")
    aruco2 = cv2.imread("home/calibration/aruco2.png")
    aruco3 = cv2.imread("home/calibration/aruco3.png")  
    
    arucoFrame[projected_coords[0][1]:projected_coords[0][1]+aruco0.shape[0], projected_coords[0][0]:projected_coords[0][0]+aruco0.shape[1]] = aruco0
    arucoFrame[projected_coords[1][1]:projected_coords[1][1]+aruco1.shape[0], projected_coords[1][0]:projected_coords[1][0]+aruco1.shape[1]] = aruco1
    arucoFrame[projected_coords[2][1]:projected_coords[2][1]+aruco2.shape[0], projected_coords[2][0]:projected_coords[2][0]+aruco2.shape[1]] = aruco2
    arucoFrame[projected_coords[3][1]:projected_coords[3][1]+aruco3.shape[0], projected_coords[3][0]:projected_coords[3][0]+aruco3.shape[1]] = aruco3

    return arucoFrame 

def findArucoMarkers(img, markerSize=4, totalMarkers=250,draw=True):
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    key = getattr(aruco,f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    bboxs, ids, _ = aruco.detectMarkers(imgGray, arucoDict, parameters=arucoParam)
    # print(ids,bboxs)
    coords = []
    if (ids is None):
        print("0 aruco patterns detected out of 4")
    elif(ids.size != 4):
        print("%s aruco patterns detected out of 4" % ids.size)
    else:
        print("%s aruco patterns detected out of 4" % ids.size)
        #converting NumPy arrays into a int list + sort aruco patterns in order
        ids = [i[0] for i in ids.tolist()]
        coords = [bboxs[i][0][0].tolist() for i in range(len(ids))]
        coords = [[int(a),int(b)] for a,b in coords]
        sorted_pairs = sorted(zip(ids, coords))
        tuples = zip(*sorted_pairs)
        ids, coords = [ list(tuple) for tuple in  tuples]
        # print(ids)
        # print(coords)
    return coords

background = drawArucoFrame()
cv2.imshow('Pool',background)
cv2.waitKey(80)

frame = get_frame()
coords = findArucoMarkers(frame)

if len(coords) == 4:
    detected_coords = coords
else: #select manually
    print('Manual Calibration required')
    for x,y in pool_coords:
        cv2.circle(frame, (x,y), 20, (0,0,255), -1)

    l_circle=detected_coords
    cv2.imshow('Pool',frame)

    cv2.setMouseCallback('Pool',draw_circle)

    background = frame.copy()
    for i,p1 in enumerate(l_circle):
        p1=tuple(p1)
        for p2 in l_circle[i+1:]:
            p2=tuple(p2)
            cv2.line(frame,p1,p2,(255,0,0),3)
        cv2.circle(frame,p1,20,(0,0,255),-1)

    cv2.imshow('Pool',frame)

    cv2.waitKey(0)
    while len(l_circle)<4:
        cv2.waitKey(0)

    cv2.setMouseCallback('Pool', lambda *args: None)
        
    detected_coords=l_circle.copy()

    frame_projector = background.copy()
    for p1 in detected_coords:
        cv2.circle(frame_projector, tuple(p1), 40, (0, 0, 255), -1)
    
############### Ordering points and format ###############

def ordering(l_point1, l_point2):

    global background
    
    l_distance_ordered=[]
    for l_ordering in permutations(list(range(len(l_point1)))):
        d=0
        l_ordered_point=[]
        for i1,i2 in enumerate(l_ordering):
            d+=np.linalg.norm(np.array(l_point1[i1])
                              - np.array(l_point2[i2]))
            l_ordered_point+=[l_point2[i2]]
        
        l_distance_ordered+=[[d,l_ordered_point]]

    l_ordered_point=min(l_distance_ordered, key=lambda x: x[0])[1]

    frame=background.copy()
    
    for p1,p2 in zip(l_point1, l_ordered_point):
        p1=tuple(p1)
        p2=tuple(p2)
        cv2.line(frame,p1,p2,(255,0,0),3)
        cv2.circle(frame,p1,20,(0,0,255),-1)
        cv2.circle(frame,p2,20,(0,255,0),-1)

    cv2.imshow('Pool',frame)
    cv2.waitKey(2000)
    
    return l_ordered_point

pool_coords = ordering(detected_coords, pool_coords)
screen_coords = ordering(pool_coords, screen_coords)
projected_coords =  ordering(pool_coords, projected_coords)

detected_coords=np.float32(detected_coords)
pool_coords=np.float32(pool_coords)
screen_coords=np.float32(screen_coords)
projected_coords=np.float32(projected_coords)

# print("---- Debug ----")
# print("screen coords : ", screen_coords)
# print("pool_coords : ", pool_coords)
# print("detected_coords : ", detected_coords)
# print("projected_coords : ",projected_coords)

############### Set projection matrix ###############

tMat1_0 = cv2.getPerspectiveTransform(screen_coords, projected_coords)
tMat1_1 = cv2.getPerspectiveTransform(detected_coords, projected_coords)
tMat1_2 = cv2.getPerspectiveTransform(projected_coords, pool_coords)
projection_matrix = tMat1_1.dot(tMat1_2).dot(tMat1_0)

poolFocus_matrix = cv2.getPerspectiveTransform(pool_coords, screen_coords)

############### Calibration Test ###############

calibration_test2=np.zeros((1080,1920,3), np.uint8)
for i,p1 in enumerate(screen_coords):
    p1=tuple(map(int, p1))
    for p2 in screen_coords[i+1:]:
        p2=tuple(map(int, p2))
        cv2.line(calibration_test2,p1,p2,(255,255,255),3)
    cv2.circle(calibration_test2,p1,40,(255,255,255),-1)

cv2.putText(calibration_test2,
            "Image 2D a deformer dans un espace 3D pour fitter le Pool, auppuyez sur une touche pour continuer",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)
cv2.imshow('Pool', calibration_test2)
cv2.waitKey(0)

test_1 = cv2.warpPerspective(calibration_test2, projection_matrix, (1920,1080), flags=cv2.INTER_LINEAR)
cv2.putText(test_1,
            "Image 2D deforme dans un espace 3D, auppuyez sur une touche pour continuer",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)
cv2.imshow('Pool',test_1)
cv2.waitKey(0)

test_2 = cv2.warpPerspective(frame_camera, poolFocus_matrix, (1920,1080), flags=cv2.INTER_LINEAR)
cv2.putText(test_2,
            "Image 3D du Pool déformer pour passer dans l'espace 2D de l'écran, auppuyez sur une touche pour continuer",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1/2,
            (0,0,255),
            1,
            cv2.LINE_AA)
cv2.imshow('Pool',test_2)
cv2.waitKey(0)

############### Export Data in json file ###############

d_information={"projection_matrix": projection_matrix,
               "poolFocus_matrix": poolFocus_matrix,
               "detected_coords": detected_coords.astype('int'),
               "pool_coords": pool_coords.astype('int'),
               "screen_coords": screen_coords.astype('int')
        }

d_information={k:v.tolist() for k,v in d_information.items()}

with open('home/calibration/calibration_data.json', 'w') as f:
    json.dump(d_information, f, indent=4)

print("calibration terminée")

cv2.destroyAllWindows()
exit()